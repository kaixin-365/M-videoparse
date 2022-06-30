<template>
  <v-main>
    <v-container>
      <v-row>
        <v-col md="6" cols="12">
          <v-card>
            <v-card-title>视频外链解析工具（由开心就好-_-维护）</v-card-title>
            <v-card-text>
              <p>本工具使用各大视频平台的API动态解析视频链链接，使用此工具可以解决外站视频直链过期失效问题，目前支持的视频平台：微博，哔哩哔哩，百度贴吧。</p>
              <p>此外尝试新增 蓝奏云盘 解析给音乐投稿者使用，使用方法参照<a href="/#/about" target="_blank">关于</a>页面</p>
              <p>微博平台支持4K、2k清晰度外链，前提是这个视频有4K或者2K清晰度,详情请看<a href="/#/about" target="_blank">关于</a></p>
              <p>
                更多信息请移步“<a href="/#/about" target="_blank">关于</a>”
              </p>
              <v-form ref="form">
                <v-select
                  :items="select"
                  v-model="now"
                  label="视频来源"
                  :rules="rules"
                ></v-select>
                <v-text-field
                  label="视频链接"
                  :placeholder="getExample()"
                  :rules="rules"
                  v-model="url"
                  :error-messages="errmsg"
                ></v-text-field>
              </v-form>
            </v-card-text>
            <v-card-actions>
              <v-btn block color="#6ebdf6" @click="submit">解析</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
        <v-col md="6" cols="12">
          <v-card>
            <v-card-title> 解析结果 </v-card-title>

            <v-card-text>
              <p>链接：{{ vurl }}</p>

              <video width="100%" :src="vurl" controls></video>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<script>
import Server from "@/networker/server";
export default {
  components: {
  },
  data() {
    return {
      //当前选择的站点
      now: "",
      //当前输入的视频地址
      url: "",
      //定义解析站点列表
      //名称:{example:"链接示例",
      //      reg:"匹配视频id的正则"}
      list: {
        '微博': {
          example: "https://weibo.com/tv/show/1034:460660553541227",
          reg: /\d{4}:\d+/,
          path: "/weibo/"
        },
        '哔哩哔哩': {
          example: "https://www.bilibili.com/video/BV1zs411S7sz",
          reg: /[aAbBvV]{2}[A-Za-z0-9\\[?=\]?]{1,}/,
          path: "/bili/"
        },
        '百度贴吧': {
          example: "https://tieba.baidu.com/p/7900324069",
          reg: /[0-9]+/,
          path: "/tieba/"
        },
      },
      rules: [(v) => !!v || "必填"],
      errmsg: "",
      //视频链接
      vurl: "请先输入地址",
    };
  },
  methods: {
    getExample() {
      return this.now ? this.list[this.now].example : "请选择视频来源";
    },
    submit() {
      console.log(this.validate());
      //验证表单
      if (this.validate()) {
        //取出视频id
        let vids = this.url.match(this.list[this.now].reg);
        if (!vids) {
          this.errmsg = "请输入正确的链接";
        } else {
          this.errmsg = "";
        }
        
        this.vurl = Server.server + this.list[this.now]["path"] + vids;
      }
    },
    validate() {
      return this.$refs.form.validate();
    },
  },
  computed: {
    select() {
      //通过遍历list获得select标签的选项
      let array = [];
      for (const key in this.list) {
        if (Object.hasOwnProperty.call(this.list, key)) {
          array.push(key);
        }
      }
      return array;
    },
  },
};
</script>

<style>
</style>