<template>
  <v-main>
    <v-container>
      <v-row>
        <v-col md="12" cols="24">
          <v-card>
            <v-card-title>关于本站</v-card-title>
            <v-card-text>
              <p>权利声明：本站不提供任何视听上传服务，所有内容均来自正规视频站点所提供的公开引用资源。</p>
              <p>运营声明：本站不保证绝对的稳定性，例如服务器遭受攻击下线等，对此介意者请使用官方投稿通道。</p>
              <p>关于隐私：本站服务器端会收集必要的信息，如IP地址，UA信息等，来分析访问情况、优化访问体验。介意者请关闭并停止使用本站。</p>
              <p>关于老版本外链接口：老版本接口不会下线，因为<a href="//github.com/ChenDoXiu" target="_blank">作者@陈独秀ChenDoXiu</a>选择闭源，所以不会再维护，敬请谅解。</p>
              <p>前端使用项目：<a href="//github.com/ChenDoXiu/MfunsTool" target="_blank">项目地址</a>,在此表示感谢！</p>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col md="12" cols="24">
          <v-card>
              <v-card-title>外链使用常见问题</v-card-title>
            <v-card-text>
              <p>关于微博外链的一些问题：</p>
              <p>4K、2K视频怎么投稿：</p>
              <p>4K视频在链接后面加 ?q=4k ，2K视频在链接后面加 ?q=2k，默认生成1080p及其以下清晰度的视频。注意问号是英文的<br>
              例：https://video_api.kms233.com/weibo/1034:4738314251731108?q=4k</p>
              <br>
              <p>关于哔哩外链的一些问题：</p>
              <p>如何指定视频的某一个分P外链：在链接后面加 ?p=P号 ，注意问号是英文的<br>
                例:https://video_api.kms233.com/bili/BV1d34y1C78W?p=2</p>
              <br>
              <p>关于蓝奏云外链的一些问题：</p>
              <p>外链格式：https://video_api.kms233.com/lanzou/?url={这里输入文件分享链接}&p={这里输入分享密码}</p>
              <p>例：https://video_api.kms233.com/lanzou/?url=https://wws.lanzouf.com/iE7vmzjrkij&p=9npv</p>
              <p>2020-2022 开心就好-_-</p>
            </v-card-text>
          </v-card>
        </v-col>
        
      </v-row>
    </v-container>
  </v-main>
</template>
<script>
export default {
    name : 'About',
    data() {
        return {
        };
    },
    mounted() {

    },
    methods() {

    },
}
</script>
