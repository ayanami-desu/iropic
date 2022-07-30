from rest_framework import serializers
from .models import Labels, Images, Albums

class NewImageSer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ('edit_time', 'origin_file', 'webp_file', 'md5', 'origin_filename', 'file_type', 'belong_album')

class ImageInfoSer(serializers.ModelSerializer):
    images_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    belong_album = serializers.ReadOnlyField(source="belong_album.name")
    class Meta:
        model = Images
        fields = ('belong_album', 'edit_time', 'labels', 'images_set')
        read_only_fields = ('belong_album', 'edit_time', )

class ImageListSer(serializers.ModelSerializer):
    belong_album = serializers.ReadOnlyField(source="belong_album.name")
    class Meta:
        model = Images
        fields = ('belong_album', 'edit_time', 'labels', 'id', 'isR18')
        read_only_fields = ('belong_album', 'edit_time')
        
    def to_representation(self, instance):
        # 返回图片含有的差分数
        data = super().to_representation(instance)
        data['sub_img_num'] = instance.images_set.count()
        return data

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