<!--
 * @Author: your name
 * @Date: 2021-02-21 13:42:27
 * @LastEditTime: 2021-02-25 15:53:20
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: \html\src\components\Appbar.vue
-->
<template>
  <v-app-bar app color="#7b7ff7" dark>
    <v-app-bar-title>{{ title }}</v-app-bar-title>
    <v-spacer></v-spacer>
        <v-btn @click="toRescue('/#/about')" color="#7b7ff7" v-bind="attrs" v-on="on" depressed rounded dark>关于</v-btn>
  </v-app-bar>
</template>

<script>
export default {
  props: ["title"],
  methods: {
    toRescue(url) {
        window.open(url,"_blank");
    }
  }
};
</script>

<style>
</style>