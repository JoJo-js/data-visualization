<template>
    <div>
        <PDFCommon ref="pdfCommon" @changeHeader="handleChecChange"></PDFCommon>
      <p></p>
      <div>
        <input type="radio" id="one" value="one" v-model="num_en" @change="numChange">
        <label for="one">Choose One Table (bar chart, would clouds, scatter diagram or bubble chart)</label>
        <br>
        <input type="radio" id="two" value="two" v-model="num_en" @change="numChange">
        <label for="two">Choose Two Tables (line chart, stacked/grouped bar chart, spider chart, tree map, hierarchy tree or sankey diagram )</label>
        <br>
      </div>
      <p></p>
      <el-row v-if="num_en==='one'">
            <el-form style="text-align:left" :inline="true" :model="searchForm" class="demo-form-inline">
              <DataSelect :fatherMethod="visualization" :showtable="false"></DataSelect>
              <b style="line-height: 40px">&nbsp &nbsp &nbsp &nbsp Please select one to four valid data (no more than one lexical data)</b>
              <br>
              <el-form-item label="Table">
                <el-select v-model="table_list" value-key ='id' filterable placeholder="select" @change="tableChange">
                    <el-option v-for="item in tableOptions" :key="item" :label="item" :value="item"></el-option>
                </el-select>
            </el-form-item>
              <el-form-item label="Data">
                <el-select v-model="attr_list" value-key ='id' multiple filterable placeholder="Select" @change = 'mulproduct'>
                    <el-option v-for="item in attrOptions" :key="item.name" :label="item.name+' ('+item.type+')'" :value="item.name"></el-option>
                </el-select>
            </el-form-item>
              <el-button type="primary" @click="attributeChange">Submit</el-button>
            </el-form>
        </el-row>
      <el-row v-else-if="num_en==='two'">
            <el-form style="text-align:left" :inline="true" :model="searchForm" class="demo-form-inline">
              <DataSelect :fatherMethod="visualization" :showtable="false"></DataSelect>

              <el-form-item label="Table1">
                <el-select v-model="table_list" value-key ='id' filterable placeholder="select" @change="tableChange">
                    <el-option v-for="item in tableOptions" :key="item" :label="item" :value="item"></el-option>
                </el-select>
            </el-form-item>
              <b style="line-height: 40px">&nbsp &nbsp &nbsp &nbsp Please select one numeric data</b>
<!--              <el-form-item label="Data">-->
<!--                <el-select v-model="attr_list" value-key ='id' multiple filterable placeholder="Select" @change = 'mulproduct'>-->
<!--                    <el-option v-for="item in attrOptions" :key="item.name" :label="item.name" :value="item.name"></el-option>-->
<!--                </el-select>-->
<!--            </el-form-item>-->
              <br>
              <el-form-item label="Table2">
                <el-select v-model="table_list2" value-key ='id' filterable placeholder="select" @change="tableChange2">
                    <el-option v-for="item in tableOptions2" :key="item" :label="item" :value="item"></el-option>
                </el-select>
            </el-form-item>
              <el-form-item label="Data">
                <el-select v-model="attr_list2" value-key ='id' multiple filterable placeholder="Select" @change = 'mulproduct2'>
                    <el-option v-for="item in attrOptions2" :key="item.name" :label="item.name+' ('+item.type+')'" :value="item.name"></el-option>
                </el-select>
            </el-form-item>
              <el-button type="primary" @click="attributeChange">Submit</el-button>
            </el-form>
        </el-row>
      <div v-if="judge_pic.length > 0">
          <div v-if="judge_pic[0]">
            <el-button v-for="item in judge_pic[1]" :key="item" @click="create_pic(item)" :title="item">
                  <i class="iconfont" v-html="item"></i>
            </el-button>
<!--            <div v-for="item in judge_pic[1]" >-->
<!--                <input type="radio" id="item" value="item" v-model="num_en">-->
<!--                <label for="item">{{item}}</label>-->
<!--            </div>-->
          </div>
          <div v-else>
            <h1 style="color:red;text-align:center">{{ judge_pic[1].toString() }}</h1>
          </div>
      </div>
      <p></p>
      <el-row v-if="searchForm.pic_type">
        <div v-if="searchForm.table.length===1" style="text-align:center"> <h2>{{this.searchForm.table[0]}}</h2></div>
        <div v-if="searchForm.table.length===2" style="text-align:center"> <h2>{{this.searchForm.table[0]}} and {{this.searchForm.table[1]}}</h2></div>
        <div v-if="data_limit" style="text-align:center"> <h1>{{data_limit}}</h1></div>
          <el-col :span="23"><div id="picture" :style="{ align:' center ',width: '100%', height: '500px',display : 'block'}"></div></el-col>

        </el-row>
    </div>
</template>

<script>
import PDFCommon from '../PDFCommon.vue'
import DataSelect from '../DataSelect.vue'
import ehcartsUtils from '../EChartsUtils'
// import * as d3 from 'd3'
// import { legendColor } from 'd3-svg-legend'

// import {Runtime, Inspector} from "@observablehq/runtime";
// import define_scatterplot from "@d3/scatterplot";
// import define_legend  from "@d3/color-legend";


export default {
  name: 'visualization',
  components:{
    PDFCommon,DataSelect
  },

  data () {
    return {
      title: "visualization",
      chartData:[],
      searchForm:{
          database:"",
          table:[],
          attr:[],
          pic_type:""
      },
      headerData:[],
      tableData:[],
      num_en: null,
      attr_list:[],
      attr1:[],
      attr2:[],
      table_list:'',
      data_limit:'',
      attr_list2:[],
      table_list2:'',
      tableOptions: [],
      tableOptions2:[],
      attrOptions: [],
      attrOptions2: [],
      judge_pic:[],
    }
  },
  mounted(){
    this.$store.state.database = ''
    this.$store.state.database = ''
  },
  methods: {
    initData(){
        console.log('------子组件调用我了---------', this.$store.state.table)
        this.headerData=[],
        this.tableData=[]
        this.table_list = ''
        this.attr_list = []
        this.attr_list2 = []
        this.table_list2 = ''
        this.tableOptions2 = []
        this.attrOptions = []
        this.attrOptions2 = []
        this.tableOptions = []
        this.judge_pic = []
        this.searchForm.table = []
        this.searchForm.attr = []
        this.searchForm.pic_type = ''
        // this.visualization()
    },


    async visualization(){
          this.searchForm.database = this.$store.state.database
          let res =await this.$httpf.vstable({"database_code":this.searchForm.database},true)
          if(res.code==0){

              this.tableOptions = res.data
          }

          // this.searchForm.table = this.$store.state.table
          // this.attrOptions = this.searchForm.table
      // console.log(this.attrOptions)

      },
    async numChange(value){
        // this.$store.commit('platform',{"value":value, "type":"table"})
        this.tableOptions2 = []
        this.attrOptions = []
        this.attrOptions2 = []
        this.attr_list = []
        this.attr_list2 = []
        this.table_list2 = ''
        this.table_list = ''
        this.searchForm.table = []
        this.searchForm.attr = []
        this.searchForm.pic_type = ''
        this.judge_pic = []

        // console.log(value)
    },
    async tableChange(value){
        // this.$store.commit('platform',{"value":value, "type":"table"})
        this.tableOptions2 = []
        this.attrOptions = []
        this.attrOptions2 = []
        this.attr_list = []
        this.attr_list2 = []
        this.table_list2 = ''
        this.searchForm.table = []
        this.searchForm.pic_type = ''
        this.judge_pic = []
        this.searchForm.table.push(value)
        let res_table =await this.$httpf.attributeList({"value":value,"database":this.searchForm.database},true)
      console.log(res_table)
          if(res_table.code==0){
              this.attrOptions = res_table.data
              // res_table.data.forEach(e =>{
              //     this.attrOptions.push({'name':e.name,'type':e.type})
              // })
          }
        if(this.num_en=='two'){
          let res_table =await this.$httpf.vstable2({"value":value},true)
          this.tableOptions2 = res_table.data
        }

        // console.log(value)
    },
    async tableChange2(value){
          // this.$store.commit('platform',{"value":value, "type":"table"})
          this.attrOptions2 = []
          this.attr_list2 = []
          this.searchForm.pic_type = ''
          this.judge_pic = []
          if(this.searchForm.table.length > 1){
            this.searchForm.table[1] = value.split('(')[0]
          }else{
            this.searchForm.table.push(value.split('(')[0])
          }
          let res_table =await this.$httpf.attributeList({"value":value,"database":this.searchForm.database},true)

            if(res_table.code==0){
                this.attrOptions2 = res_table.data
                // res_table.data.forEach(e =>{
                //     this.attrOptions.push({'name':e.name,'type':e.type})
                // })
            }
          // console.log(this.searchForm.table)
      },
      async mulproduct(value){
        //   console.log('!!!!'+value.length)
        //   console.log(this.attr_list)
        // console.log(this.attr_list)
        this.searchForm.attr = []
        this.attr1 = []
        this.searchForm.pic_type = ''
        this.judge_pic = []
        this.searchForm.attr = this.attr2.slice(0)
          value.forEach(e=>{
              this.searchForm.attr.push(this.table_list+ '+'+ e)
              this.attr1.push(this.table_list+ '+'+ e)
          })
        // console.log(this.searchForm.attr)
      },
    async mulproduct2(value){
      //   console.log('!!!!'+value.length)
      //   console.log(this.attr_list)
      //   this.searchForm.attr.push(value[value.length-1])
      this.searchForm.attr = this.attr1.slice(0)
      this.attr2 = []
      this.searchForm.pic_type = ''
      this.judge_pic = []
      // console.log(this.searchForm.attr)
      value.forEach(e=>{
            this.searchForm.attr.push(this.table_list2.split('(')[0]+ '+'+ e)
            this.attr2.push(this.table_list2.split('(')[0]+ '+'+ e)
        })
      // console.log(this.searchForm.attr)
    },
    async attributeChange(){
      this.searchForm.pic_type = ''
      let res =await this.$httpf.judgepic(this.searchForm,true)
      this.judge_pic = res.data
    },
    async create_pic(value){
      this.searchForm.pic_type = value
      let res =await this.$httpf.picdata(this.searchForm,true)
      if (res.code==0){
        await this.create_picture(res.data)
      }
    },

    async create_picture(d){
      // console.log(d)
      this.data_limit = ''
      if(this.searchForm.pic_type=='Bar Chart'){
        let draw = this.$echarts.init(document.getElementById('picture'))
        draw.clear();
        this.bar_chart(draw, d)
      }else if(this.searchForm.pic_type=='Word Clouds'){
        let draw = this.$echarts.init(document.getElementById('picture'))
        draw.clear();
        this.word_clouds(draw, d)
      }else if(this.searchForm.pic_type=='Scatter Diagram'){
        this.scatter_diagram(d)
      }else if(this.searchForm.pic_type=='Bubble Charts'){
        this.bubble_charts(d)
      }else if(this.searchForm.pic_type=='Tree Map'){
        this.tree_map(d)
      }else if(this.searchForm.pic_type=='Hierarchy Tree'){
        this.hierarchy_tree(d)
      }else if(this.searchForm.pic_type=='Line Chart'){
        this.line_chart(d)
      }else if(this.searchForm.pic_type=='Stacked Bar Chart'){
        this.stacked_bar_chart(d)
      }else if(this.searchForm.pic_type=='Grouped Bar Chart'){
        this.grouped_bar_chart(d)
      }else if(this.searchForm.pic_type=='Spider Chart'){
        let draw = this.$echarts.init(document.getElementById('picture'))
        draw.clear();
        this.spider_chart(draw, d)
      }else if(this.searchForm.pic_type=='Sankey Diagram'){
        this.sankey_diagram(d)
      }

    },

    sankey_diagram(data){
      google.charts.load('current', {packages:['sankey']});
      var dataTable = new google.visualization.DataTable();
      dataTable.addColumn('string', data[0][0]);
      dataTable.addColumn('string', data[0][1]);
      dataTable.addColumn('number', data[0][2]);

      let d = []
      data[1].forEach(e=>{
        d.push([e[0],e[1],e[2]])
      })
      if(d.length>30){
          d = d.slice(0,30)
        this.data_limit = 'Just show 30 instances'
        }

      dataTable.addRows(d);
      // console.log(dataTable)
      var options = {

    };

      let chart = new google.visualization.Sankey(document.getElementById('picture'));
      chart.draw(dataTable, options);
    },

    spider_chart(draw, data){
      let year = [];
      let name = [];
      let value = [];
      data[1].forEach(e=>{
          if(!year.includes(e[1])){
            year.push(e[1])
          }
          if(!name.includes(e[0])){
            name.push(e[0])
          }
      })
      year.sort(function(a,b){return a-b})
      let ind = []
      year.forEach(e=>{
        ind.push({name: e.toString()})
      })
      name.forEach(e=>{
        let v = new Array(year.length)
        for(let i=0;i<data[1].length;i++){
          for(let j=0;j<year.length;j++){
            if(data[1][i][1]==year[j]&&data[1][i][0]==e){
              v[j] = data[1][i][2]
            }
          }
        }
        value.push({
          name: e,
          value: v
        })
      })
      if(name.length==10){
        this.data_limit = 'Just show 10 instances'
      }

      // console.log(x,y)
      var option = {
        legend: {
          data: name
        },
        tooltip: {},
        radar: {
          // shape: 'circle',
          indicator: ind
        },
        series: [
          {
            type: 'radar',
            data: value
          }
        ]
      };

      draw.setOption(option)
    },

    grouped_bar_chart(data){
      google.charts.load('current', {packages: ['corechart', 'bar']});

      var dataTable = new google.visualization.DataTable();
      dataTable.addColumn('string', data[0][0]);
      let year = []
      let name = []
      data[1].forEach(e=>{
        if(! year.includes(e[1])){
          year.push(e[1])
        }
        if(! name.includes(e[0])){
          name.push(e[0])
        }
      })
      let d = []
      year.sort(function(a,b){return a-b})
      year.forEach(e=>{
        dataTable.addColumn('number', e.toString());
      })
      name.forEach(e=>{
        let onedata = new Array(year.length+1)
        onedata[0] = e
        for(let j=0;j<year.length;j++){
          for(let k=0;k<data[1].length;k++){
            if(data[1][k][1]==year[j] && data[1][k][0]==e){
              onedata[j+1] = data[1][k][2]
            }
          }
        }
        d.push(onedata)
      })
      if(d.length==10){
        this.data_limit = 'Just show 10 instances'
      }

      // console.log(dataTable)
      // console.log(d)

      dataTable.addRows(d);
      // console.log(dataTable)
      var options = {

          hAxis: {title: data[0][1]},
          vAxis: {title: data[0][2]},
      };

      let chart = new google.charts.Bar(document.getElementById('picture'));

      chart.draw(dataTable, google.charts.Bar.convertOptions(options));
    },

    stacked_bar_chart(data){
      google.charts.load("current", {packages:["corechart"]});

      var dataTable = new google.visualization.DataTable();
      dataTable.addColumn('string', data[0][1]);
      let name = []
      let data0 = [] //year
      data[1].forEach(e=>{
        if(! name.includes(e[0])){
          dataTable.addColumn('number', e[0]);
          name.push(e[0])
        }
        if(! data0.includes(e[1])){
          data0.push(e[1])
        }
      })
      let d = []
      data0.sort(function(a,b){return a-b})
      data0.forEach(e=>{
        let onedata = new Array(name.length+1)
        onedata[0] = e.toString()
        for(let j=0;j<name.length;j++){
          for(let k=0;k<data[1].length;k++){
            if(data[1][k][1]==e && data[1][k][0]==name[j]){
              onedata[j+1] = data[1][k][2]
            }
          }
        }
        d.push(onedata)
      })
      if(d[0].length==11){
        this.data_limit = 'Just show 10 instances'
      }
      // console.log(d)

      dataTable.addRows(d);
      // console.log(dataTable)
      var options = {
        legend: { position: 'top', maxLines: 3 },
        bar: { groupWidth: '75%' },

          hAxis: {title: data[0][2]},
          vAxis: {title: data[0][1]},
        isStacked: true
      };

      let chart = new google.visualization.BarChart(document.getElementById('picture'));

      chart.draw(dataTable, options);
    },

    line_chart(data){
      google.charts.load('current', {packages:['corechart']});

      var dataTable = new google.visualization.DataTable();
      dataTable.addColumn('string', data[0][1]);
      let name = []
      let data0 = [] //year
      data[1].forEach(e=>{
        if(! name.includes(e[0])){
          dataTable.addColumn('number', e[0]);
          name.push(e[0])
        }
        if(! data0.includes(e[1])){
          data0.push(e[1])
        }
      })
      let d = []
      data0.sort(function(a,b){return a-b})
      data0.forEach(e=>{
        let onedata = new Array(name.length+1)
        onedata[0] = e.toString()
        for(let j=0;j<name.length;j++){
          for(let k=0;k<data[1].length;k++){
            if(data[1][k][1]==e && data[1][k][0]==name[j]){
              onedata[j+1] = data[1][k][2]
            }
          }
        }
        d.push(onedata)
      })
      if(d[0].length == 11){
        this.data_limit = 'Just show 10 instances'
      }

      dataTable.addRows(d);
      // console.log(dataTable)
      var options = {

          hAxis: {title: data[0][1]},
          vAxis: {title: data[0][2]},
          showScale: true,

      };

      let chart = new google.visualization.LineChart(document.getElementById('picture'));

      chart.draw(dataTable, options);
    },

    hierarchy_tree(data){
      google.charts.load('current', {packages:['wordtree']});

          // [ ['Phrases'],
          //   ['cats are better than dogs'],
      var dataTable = new google.visualization.DataTable();
        dataTable.addColumn('string', data[0][0]);
        dataTable.addColumn('number', data[0][2]);
        let d = []
        data[1].forEach(e=>{
          d.push([this.searchForm.table[0]+' '+e[0]+' '+e[1],e[2]])
        })
      console.log(d)
        dataTable.addRows(d);
        // console.log(dataTable)

        var options = {
          wordtree: {
            format: 'implicit',
            word: this.searchForm.table[0]
          }
        };
        // console.log(options)

        let chart = new google.visualization.WordTree(document.getElementById('picture'));
        chart.draw(dataTable, options);

    },

    tree_map(data){
      google.charts.load('current', {packages:['treemap']});

          // ['Location', 'Parent', 'Market trade volume (size)', 'Market increase/decrease (color)'],
          // ['Global',    null,                 0,                               0],

      var dataTable = new google.visualization.DataTable();
        dataTable.addColumn('string', data[0][0]);
        dataTable.addColumn('string', data[0][1]);
        dataTable.addColumn('number', data[0][2]);
      if(data[0].length==4){
        dataTable.addColumn('number', data[0][3]);
      }else{
        dataTable.addColumn('number', '');
      }
      let d = [[this.searchForm.table[0], null, 0, null]]
        data[1].forEach(e=>{
          let flag = true
          for(let k=0;k<d.length;k++){
            if(d[k][0]==e[0]){
              flag=false
            }
          }
          if(flag) d.push([e[0], this.searchForm.table[0], 0, 0])
          if(e.length==4){
            d.push([e[1], e[0], e[2], e[3]])
          }else{
            d.push([e[1], e[0], e[2], e[2]])
          }
        })
      dataTable.addRows(d);
      var options = {
        midColor: 'rgb(175,241,239)',
        minColor: 'rgb(94,181,227)',
        maxColor: '#3a4ab2',
        headerHeight: 15,
        fontColor: 'black',
        showScale: true,
        generateTooltip: showFullTooltip
        };
      function showFullTooltip(row, size, value) {
    return '<div style="background:#fd9; padding:10px; border-style:solid">' +
           '<span style="font-family:Courier"><b>' + dataTable.getValue(row, 0) +
           '</b>, ' +'<br>' +
	   dataTable.getColumnLabel(2) +
           ' : ' + size +'<br>' + dataTable.getColumnLabel(3) + ': ' + value + '</div>';
  }


      let tree = new google.visualization.TreeMap(document.getElementById('picture'));

      tree.draw(dataTable, options)

    },

    scatter_diagram(data) {
      // Define the chart to be drawn.


      google.charts.load('current', {packages: ['corechart']});
      let att = this.judge_pic[2]
      let lex = []
      let num = []
      att.forEach((e, i)=>{
        if(e[1] == 'lexical'){
          lex.push(i)
        }else{
          num.push(i)
        }
      })
      var dataTable = new google.visualization.DataTable();
      if(num.length+lex.length == 2){
        dataTable.addColumn('string', data[0][0]);
        dataTable.addColumn('number', data[0][1]);
        dataTable.addColumn('number', data[0][2]);
      }else{
        if(lex.length==1){
          dataTable.addColumn('string', data[0][0]);
          dataTable.addColumn('number', data[0][num[0]+1]);
          dataTable.addColumn('number', data[0][num[1]+1]);
          dataTable.addColumn('string', data[0][lex[0]+1]);
        }else{
          dataTable.addColumn('string', data[0][0]);
          dataTable.addColumn('number', data[0][1]);
          dataTable.addColumn('number', data[0][2]);
          dataTable.addColumn('number', data[0][3]);
        }
      }
        // A column for custom tooltip content
        // dataTable.addColumn({type: 'string', role: 'tooltip'});
        let d = []
        data[1].forEach(e=>{
          if(e.length==3){
            d.push([e[0], e[1],e[2]])
          }else{
            if (lex.length==1){
              d.push([e[0], e[num[0]+1],e[num[1]+1],e[lex[0]+1]])
            }else{
              d.push([e[0], e[1],e[2],e[3]])
            }
          }

        })
        dataTable.addRows(d);
        // let x_min = Math.min.apply(null, data.map(function (e) { return e[1]}))
        // let x_max = Math.max.apply(null, data.map(function (e) { return e[1]}))
        // let y_min = Math.min.apply(null, data.map(function (e) { return e[2]}))
        // let y_max = Math.max.apply(null, data.map(function (e) { return e[2]}))
      if(num.length+lex.length == 2){
        var options = {
          legend: 'none',
          tooltip: {isHtml: true},
          hAxis: {title: data[0][num[0]+1]},
          vAxis: {title: data[0][num[1]+1]},
          bubble: {textStyle: {fontSize: 8, color: 'none'}},
          sizeAxis:{maxSize:4,minSize:4},
          colorAxis: {colors: ['#e7711c', '#4374e0']}
        };
      }else{
        var options = {
          tooltip: {isHtml: true},
          hAxis: {title: data[0][num[0]+1]},
          vAxis: {title: data[0][num[1]+1]},
          bubble: {textStyle: {fontSize: 8, color: 'none'}},
          sizeAxis:{maxSize:4,minSize:4},
          colorAxis: {colors: ['#e7711c', '#4374e0']}
        };
      }


        let chart = new google.visualization.BubbleChart(document.getElementById('picture'));
        chart.draw(dataTable, options);


    },

    bubble_charts(data) {
      // Define the chart to be drawn.

      google.charts.load('current', {packages: ['corechart']});
      let att = this.judge_pic[2]
      let lex = []
      let num = []
      att.forEach((e, i)=>{
        if(e[1] == 'lexical'){
          lex.push(i)
        }else{
          num.push(i)
        }
      })
      var dataTable = new google.visualization.DataTable();
      if(num.length+lex.length == 3){
        dataTable.addColumn('string', data[0][0]);
        dataTable.addColumn('number', data[0][1]);
        dataTable.addColumn('number', data[0][2]);
        dataTable.addColumn('string', '');
        dataTable.addColumn('number', data[0][3]);
      }else{
        if(lex.length==1){
          dataTable.addColumn('string', data[0][0]);
          dataTable.addColumn('number', data[0][num[0]+1]);
          dataTable.addColumn('number', data[0][num[1]+1]);
          dataTable.addColumn('string', data[0][lex[0]+1]);
          dataTable.addColumn('number', data[0][num[2]+1]);
        }else{
          dataTable.addColumn('string', data[0][0]);
          dataTable.addColumn('number', data[0][1]);
          dataTable.addColumn('number', data[0][2]);
          dataTable.addColumn('number', data[0][3]);
          dataTable.addColumn('number', data[0][4]);
        }
      }
        // A column for custom tooltip content
        // dataTable.addColumn({type: 'string', role: 'tooltip'});
        let d = []
        data[1].forEach(e=>{
          if(e.length==4){
            d.push([e[0], e[1],e[2],'', e[3]])
          }else{
            if (lex.length==1){
              d.push([e[0], e[num[0]+1],e[num[1]+1],e[lex[0]+1], e[num[2]+1]])
            }else{
              d.push([e[0], e[1],e[2],e[3], e[4]])
            }
          }

        })
        dataTable.addRows(d);
        // let x_min = Math.min.apply(null, data.map(function (e) { return e[1]}))
        // let x_max = Math.max.apply(null, data.map(function (e) { return e[1]}))
        // let y_min = Math.min.apply(null, data.map(function (e) { return e[2]}))
        // let y_max = Math.max.apply(null, data.map(function (e) { return e[2]}))
        if(num.length+lex.length == 3){
            var options = {
            legend: 'none',
            tooltip: {isHtml: true},
            hAxis: {title: data[0][num[0]+1]},
            vAxis: {title: data[0][num[1]+1]},
            bubble: {textStyle: {fontSize: 8, color: 'none'}},
            sizeAxis:{maxSize:10,minSize:3},
              colorAxis: {colors: ['#e7711c', '#4374e0']}
          };
        }
        else{
          var options = {
            tooltip: {isHtml: true},
            hAxis: {title: data[0][num[0]+1]},
            vAxis: {title: data[0][num[1]+1]},
            bubble: {textStyle: {fontSize: 8, color: 'none'}},
            sizeAxis:{maxSize:10,minSize:3},
            colorAxis: {colors: ['#e7711c', '#4374e0']}
          };
        }


        let chart = new google.visualization.BubbleChart(document.getElementById('picture'));
        chart.draw(dataTable, options);

    },






// This function takes the output of 'layout' above and draw the words
// Better not to touch it. To change parameters, play with the 'layout' variable above
    word_clouds(draw, data) {
      let x = [];
        data[1].forEach(e=>{
            x.push({'name': e[0], 'value':e[1]})
        })
        if(x.length>100){
          x = x.slice(0,100)
          this.data_limit = 'Just show 100 instances'
        }
        let option = {
          series: [{
              type: 'wordCloud',
              sizeRange: [15, 60],
              rotationRange: [-90, 90],
              rotationStep: 45,
              gridSize: 8,
              shape: 'circle',
              width: '100%',
              height: '100%',

              textStyle: {

                      color: function () {
                          return 'rgb(' + [
                              Math.round(Math.random() * 160),
                              Math.round(Math.random() * 160),
                              Math.round(Math.random() * 160)
                          ].join(',') + ')';
                       //color: function(a){return colorList[a.dataIndex]},//显示特定颜色
                      }

              },
              data: x,
            // {name: 'Farrah Abraham',
            // value: 366}
          }]
        }
        draw.setOption(option)
    },
    
    bar_chart(draw, data){
      let x = [];
      let y = [];
      data[1].forEach(e=>{
          x.push(e[0])
      })
      if(x.length>30){
        x = x.slice(0,30)
        this.data_limit = 'Just show 30 instances'
      }
      data[1].forEach(e=>{
          y.push(e[1])
      })
      if(y.length>30){
        y = y.slice(0,30)
      }
      // console.log(x,y)
      draw.setOption({
          xAxis: {name:data[0][0], data: x},
          yAxis: {name:data[0][1]},
          tooltip: {},
          legend: {data:data[0].slice(1)},
          series: [
            {
              name: data[0][1],
              type: 'bar',
              data: y
            }
          ]
      })
    },

    handleSelectionChange(value){
        this.$refs.pdfCommon.handleSelectionChangeMultiple(value,"",this.headerData)
    },
    handleChecChange(value){
        this.headerData = value
    },
    removeDuplicationData(value){
        this.chartData.forEach((item, index) =>{
            if(item.id == value.id){
                this.chartData.splice(index, 1);
            }
        })
        this.chartData.push(value)
    }
  }
}
</script>