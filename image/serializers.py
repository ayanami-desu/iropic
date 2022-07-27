from rest_framework import serializers
from .models import Labels, Images, Albums

class NewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        exclude = ('labels',)
        #fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    belong_to_album = serializers.ReadOnlyField(source="belong_to_album.name")
    class Meta:
        model = Images
        fields = ('belong_to_album', 'edit_time', 'labels', 'origin_filename', 'author')
        read_only_fields = ('belong_to_album', 'edit_time', )

class ImageListSerializer(serializers.ModelSerializer):
    belong_to_album = serializers.ReadOnlyField(source="belong_to_album.name")
    class Meta:
        model = Images
        fields = ('belong_to_album', 'edit_time', 'labels', 'id', 'isR18')
        read_only_fields = ('belong_to_album', 'edit_time', )

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Labels
        fields = ('name',)

    def to_representation(self, instance):
        # 返回每个标签下的图片数
        data = super().to_representation(instance)
        data['images_num'] = instance.images_set.count()
        return data

class NewAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Albums
        fields = ('name', 'desc', 'isR18')

class AlbumListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Albums
        fields = ('id', 'created_time', 'name', 'desc', 'isR18')

    def to_representation(self, instance):
        # 调用父类获取当前序列化数据，instance代表每个对象实例ob
        data = super().to_representation(instance)
        # 对序列化数据做修改，添加新的数据
        # 添加相册中的图片数
        data['images_num'] = instance.images_set.count()
        return data