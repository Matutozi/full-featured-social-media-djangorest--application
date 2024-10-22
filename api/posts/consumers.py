from .models import Post, PostComment
from .serializers import PostSerializer

from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
)
from djangochannelsrestframework.observer import model_observer
from djangochannelsrestframework.permissions import IsAuthenticated


class PostConsumer(
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    GenericAsyncAPIConsumer,
):

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    async def connect(self, **kwargs):
        await self.model_change.subscribe()
        await super().connect()

    async def disconnect(self, close):
        await self.model_change.unsubscribe()
        await super().disconnect(close)

    @model_observer(Post)
    async def model_change(self, message, observer=None, **kwargs):
        await self.send_json(dict(message.data))

    @model_change.serializer
    def model_serialize(self, instance, action, **kwargs):
        return dict(data=PostSerializer(instance=instance).data, action=action.value)
