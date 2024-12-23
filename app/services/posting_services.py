from uuid import UUID, uuid4
from datetime import datetime, timedelta

import brazilcep
import redis.asyncio as redis
from pytz import timezone
from fastapi import status, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.configs import settings
from app.models.address_model import AddressModel
from app.services.rabbitmq_publisher import RabbitmqPublisher
from app.services.rabbitmq_consumer import RabbitmqConsumer
from app.models.posting_model import PostModel, PostStatus
from app.core.database import get_session
from app.schemas.posting_schema import (
    CreatePostRequest,
    PostResponse,
    UpdatePostRequest
)


class PostingServices:

    def __init__(self, db: AsyncSession = Depends(get_session)):
        self.db = db
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )


    @staticmethod
    def rabbitmq_consumer(queue_name: str):
        queue = queue_name
        if not queue:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Configuração do RabbitMQ inválida. Verifique as variáveis de ambiente."
            )
        rabbitmq_consumer = RabbitmqConsumer(queue)

        return rabbitmq_consumer

    @staticmethod
    def rabbitmq_publisher(exchange: str, routing_key: str, queue: str):
        exchange, routing_key, queue = exchange, routing_key, queue
        if not exchange or not routing_key or not queue:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Configuração do RabbitMQ inválida. Verifique as variáveis de ambiente."
            )
        rabbitmq_publisher = RabbitmqPublisher(exchange, routing_key, queue)

        return rabbitmq_publisher

    async def create_new_post(self, post_data: CreatePostRequest, exchange: str, routing_key: str, queue: str) -> dict:
        try:
            address_returned = brazilcep.get_address_from_cep(post_data.endereco.cep)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CEP inválido ou não encontrado."
            )

        address = AddressModel(
            cep=post_data.endereco.cep,
            cidade=address_returned.get("city").upper(),
            estado=address_returned.get("uf").upper(),
            rua=address_returned.get("street").upper(),
            bairro=address_returned.get("district").upper(),
            numero=post_data.endereco.numero,
            complemento=post_data.endereco.complemento.upper(),
        )

        try:
            self.db.add(address)
            await self.db.commit()
            await self.db.refresh(address)
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao salvar o endereço. Tente novamente mais tarde. Erro: {e}"
            )

        current_time = datetime.now(tz=timezone("America/Sao_Paulo"))

        historico_atualizacoes = {
            current_time.strftime("%d/%m/%Y %H:%M:%S"): PostStatus.CRIADO.value
        }

        while True:
            codigo_rastreamento = uuid4()
            query = await self.db.execute(
                select(PostModel).where(PostModel.codigo_rastreamento == codigo_rastreamento)
            )
            existent_post = query.scalars().first()
            if not existent_post:
                break

        post = PostModel(
            endereco_id=address.id,
            email=post_data.email.upper(),
            peso=post_data.peso,
            altura=post_data.altura,
            largura=post_data.largura,
            comprimento=post_data.comprimento,
            transportadora=post_data.transportadora.upper(),
            historico_atualizacoes=historico_atualizacoes,
            data_criacao=current_time,
            status_postagem=PostStatus.CRIADO,
            previsao_entrega=current_time + timedelta(days=20),
            codigo_rastreamento=codigo_rastreamento
        )

        post.volume = post_data.altura * post_data.largura * post_data.comprimento

        valor_frete = 20
        if post.peso > 5:
            peso_excedente = post.peso - 5
            valor_frete += peso_excedente * 2

        if post.volume > 3000:
            volume_excedente = post.volume - 3000
            valor_frete += (volume_excedente // 500)

        post.valor_frete = valor_frete

        try:
            self.db.add(post)
            await self.db.commit()
            await self.db.refresh(post)

            rabbitmq_publisher = self.rabbitmq_publisher(exchange, routing_key, queue)
            await rabbitmq_publisher.send_message({
                "action": "post_created",
                "data": {
                    "id": post.id,
                    "email": post.email,
                    "codigo_rastreamento": str(post.codigo_rastreamento),
                    "transportadora": post.transportadora
                }
            })
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao salvar no banco. Tente novamente mais tarde. Erro: {e}"
            )

        return {
            "status_code": status.HTTP_201_CREATED,
            "message": "Postagem criada com sucesso.",
            "data": PostResponse.from_model(post)
        }

    async def get_post_info(self, tracking_code: UUID) -> dict:
        cached_post = await self.redis.get(str(tracking_code))

        if cached_post:
            return {
                "status_code": status.HTTP_200_OK,
                "message": "Postagem retornada com sucesso.",
                "data": PostResponse.model_validate_json(cached_post)
            }

        query = await self.db.execute(
            select(PostModel).where(
                PostModel.codigo_rastreamento == tracking_code
            )
        )
        post_found = query.scalars().first()

        if not post_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Não foram encontradas postagens com o código de rastreamento informado."
            )

        await self.redis.setex(
            str(tracking_code),
            300,
            PostResponse.from_model(post_found).model_dump_json()
        )

        return {
            "status_code": status.HTTP_200_OK,
            "message": "Postagem retornada com sucesso.",
            "data": PostResponse.from_model(post_found)
        }

    async def update_post(
            self,
            post_id: int,
            updated_post: UpdatePostRequest,
            exchange: str,
            routing_key: str,
            publish_queue: str
    ) -> dict:
        query = await self.db.execute(
            select(PostModel).where(PostModel.id == post_id)
        )
        existent_post = query.scalars().first()

        if not existent_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Não foram encontradas postagens com o ID informado."
            )

        if str(updated_post.status_postagem.value) == "CRIADO":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requisição inválida. Não é possível alterar o status de uma postagem já criada para o status CRIADO."
            )

        if str(existent_post.status_postagem.value) == str(updated_post.status_postagem.value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requisição inválida. A postagem já se encontra com o status {existent_post.status_postagem.value}."
            )

        if str(existent_post.status_postagem.value) == "ENTREGUE" and str(updated_post.status_postagem.value) == "EM_TRANSITO":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requisição inválida. Essa postagem já foi entregue ao destinatário."
            )

        if str(existent_post.status_postagem.value) == "CRIADO" and str(updated_post.status_postagem.value) == "ENTREGUE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requisição inválida. Essa postagem ainda não passou pelo processo de entrega."
            )

        existent_post.status_postagem = updated_post.status_postagem
        current_time = datetime.now(tz=timezone("America/Sao_Paulo"))
        current_time_as_str = current_time.strftime("%d/%m/%Y %H:%M:%S")

        new_historic = dict(existent_post.historico_atualizacoes)
        new_historic[current_time_as_str] = updated_post.status_postagem.value
        existent_post.historico_atualizacoes = new_historic

        if updated_post.status_postagem == PostStatus.EM_TRANSITO:
            existent_post.data_envio = current_time
            try:
                consumer = self.rabbitmq_consumer("created_queue")
                await consumer.consume_messages_created_queue(post_id)

                rabbitmq_publisher = self.rabbitmq_publisher(exchange, routing_key, publish_queue)
                await rabbitmq_publisher.send_message({
                    "action": "updated_post",
                    "data": {
                        "id": existent_post.id,
                        "email": existent_post.email,
                        "transportadora": existent_post.transportadora
                    }
                })

                self.db.add(existent_post)
                await self.db.commit()
                await self.db.refresh(existent_post)
            except Exception as e:
                await self.db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro: {e}"
                )

        if updated_post.status_postagem == PostStatus.ENTREGUE:
            existent_post.data_entrega = current_time
            try:
                consumer = self.rabbitmq_consumer("on_course_queue")
                await consumer.consume_messages_on_course_queue(post_id)

                self.db.add(existent_post)
                await self.db.commit()
                await self.db.refresh(existent_post)
            except Exception as e:
                await self.db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro: {e}"
                )

        cached_post = await self.redis.get(str(existent_post.codigo_rastreamento))
        if cached_post:
            await self.redis.setex(
                str(existent_post.codigo_rastreamento),
                300,
                PostResponse.from_model(existent_post).model_dump_json()
            )

        return {
            "status_code": status.HTTP_200_OK,
            "message": "Postagem atualizada com sucesso.",
            "data": PostResponse.from_model(existent_post)
        }
