<template>
  <div>

        <el-button icon="el-icon-view" @click="dialogVisible = true">PDF Preview</el-button>
        <el-dialog title="pdf preview" :visible.sync="dialogVisible" :width="dialogWidth" @opened="dialogOpend" :close-on-click-modal="false" :close-on-press-escape="false">
            <div id="printPage">
                <div v-for="(item, i) in this.$store.state.pdfData" :key="item.id">
                    <div v-if="i==0"  class = "outer_label_1" :style="{backgroundImage:'url('+require('../assets/login.jpg')+')'}"></div>
                    <el-table v-if="item.type=='table'" :data="item.data" border stripe style="width: 100%; margin-bottom: 20px;" >  <!-- :span-method="objectSpanMethod" -->
                        <!-- <el-table-column v-for="header in item.head" :prop="header.param" :key="header.label"
                                        :label="header.label" :width="header.width" header-align="center">
                        </el-table-column> -->
                        <el-table-column v-for="header in item.head" :prop="header.param" :key="header.label"
                                        :label="header.label" :width="header.width" header-align="center">
                            <template v-if="header.children">
                                <el-table-column v-for="c_header in header.children" :prop="c_header.param" :key="c_header.label" :label="c_header.label" :width="c_header.width" header-align="center">
                                </el-table-column>
                            </template>
                        </el-table-column>
                    </el-table>

                    <el-row v-if="item.num_type=='multiple'">
                        <el-col :span="12"><div :id="item.values[0].id" :style="{width: '100%', height: '500px'}"></div></el-col>
                        <el-col :span="12"><div :id="item.values[1].id" :style="{width: '100%', height: '500px'}"></div></el-col>
                    </el-row>

                    <!-- <div v-if="item.type=='echart'" :id="item.id" style='height:400px; width:100%;'></div> -->
                    <div v-if="item.num_type=='single'" :id="item.id" style='height:400px; width:100%;'></div>
                    
                    
                    <el-row>
                        <el-col :span="24">
                            <el-input v-show="!spanVisible" type="textarea" autosize placeholder="please input"  v-model="inputList[i].value"></el-input>
                            <div v-show="spanVisible" style="float:left;text-align:left;padding-bottom:15px;">
                                {{inputList[i].value}}
                            </div>
                        </el-col>
                    </el-row>
                    
                </div>
                <!-- <el-table v-for="p in this.$store.state.pdfData" :key="p"  :data="p.data" border stripe style="width: 100%; margin-bottom: 20px;" @selection-change="handleSelectionChange">
                    <el-table-column v-for="header in p.head" :prop="header.param" :key="header.label"
                                    :label="header.label" :width="header.width" header-align="center">
                    </el-table-column>
                </el-table> -->
            </div>
            <span slot="footer" class="dialog-footer">
                <el-button type="warning" @click="spanVisible = !spanVisible">Preview and Edit</el-button>
                <el-button @click="dialogVisible = false">Cancel</el-button>
                <el-button type="primary" @click="getPdf_page">Download page</el-button>
                <el-button type="primary" @click="getPdf_no_page">Download non-page</el-button>
            </span>
        </el-dialog>
  </div>
</template>
<style>
    .outer_label_1 {
        background-size: 100% 100%;
        height: 578px;
        width: 100%
    }
    
</style>
<script>
  import html2Canvas from "html2canvas";
  import JsPDF from "jspdf";
  import elementResize from 'element-resize-detector'
  export default {
    name: 'pdfcommon',
    data() {
      return {
        inputList:[{ key:'input1', label:'input1', value:'' },{ key:'input2', label:'input2', value:'' },
                   { key:'input3', label:'input3', value:'' },{ key:'input4', label:'input4', value:'' },
                   { key:'input5', label:'input5', value:'' },{key:'input6', label:'input6', value:'' },
                   {key:'input7', label:'input7', value:'' },{key:'input8', label:'input8', value:'' },
                   {key:'input9', label:'input9', value:'' },{key:'input10', label:'input10', value:'' },
                   {key:'input11', label:'input11', value:'' },{key:'input12', label:'input12', value:'' },
                   {key:'input13', label:'input13', value:'' },{key:'input14', label:'input14', value:'' },
                   {key:'input15', label:'input15', value:'' },{key:'input16', label:'input16', value:'' },
                   {key:'input17', label:'input17', value:'' },{key:'input18', label:'input18', value:'' },
                   {key:'input19', label:'input19', value:'' },{key:'input20', label:'input20', value:'' }],
        spanVisible:false,
        textarea:['textarea0', 'textarea1','textarea2','textarea3','textarea4','textarea5','textarea6','textarea7','textarea8','textarea9','textarea10'],
        dialogWidth:"80%",
        dialogVisible: false,
        checkAll: true,
        isIndeterminate: false,
        checkedList: [],
        headerData: [],
        selectedData:[],
        tableLabel : []
      }
    },
    mounted:function(){
        console.log("PDFcommon", this.$store.state.pdfData)
        this.tableLabel = this.$parent.tableLabel
        if(this.tableLabel){
            this.tableLabel.forEach(element => {
                this.checkedList.push(element.param);
            })
            this.headerData = this.tableLabel
        }
    },
    methods:{
      objectSpanMethod({ row, column, rowIndex, columnIndex }){
            if (row.rowspan && columnIndex === 0) {
                if (rowIndex === 0) {
                    return {
                        rowspan: row.maxlength,
                        colspan: 1
                    };
                } else {
                    return {
                        rowspan: 0,
                        colspan: 0
                    };
                }
            }
        },
      dialogOpend(){
        console.log(this.$store.state.pdfData)

        this.$store.state.pdfData.forEach(e =>{
            if(e.num_type=='multiple'){
                e.values.forEach(item =>{
                    if(item.type=='echart')
                        this.createLineECharts(item.id, item.title, item.legend, item.xAxis, item.yAxis, item.series)
                    else if(item.type=='radar')
                        this.createradarEcharts(item.id, item.title, item.legend, item.radar, item.series)
                     else if(item.type=='bar')
                        this.createBarEcharts(item.id, item.title, item.legend, item.xAxis, item.yAxis, item.series)
                    else if(item.type == 'line')
                        this.createLineEchartsCommon(item.id, item.title, item.legend, item.xAxis, item.yAxis, item.series)
                })
            }else{
                if(e.type=='echart')
                    this.createLineECharts(e.id, e.title, e.legend, e.xAxis, e.yAxis, e.series)
                else if(e.type == 'line')
                    this.createLineEchartsCommon(e.id, e.title, e.legend, e.xAxis, e.yAxis, e.series)
            }
            
        })
      },
      handleCheckAllChange(value){
            this.checkedList = [];
            this.headerData = [];
            if (value) {
                console.log("==true")
                this.checkAll = true
                this.tableLabel.forEach(element => {
                    this.checkedList.push(element.param);
                    this.headerData.push(element);
                });
            } else {
                console.log("==false")
                this.checkAll = false
            }
            console.log('Select All', value,this.isIndeterminate)
            this.$store.commit('pdfOperate',{"name":this.$parent.title, "type":"table", "data":this.selectedData, "head":this.headerData})
            this.$emit('changeHeader', this.headerData)
        },
        handleCheckedChange(value){
            this.checkedList = []
            this.headerData = []
            if(value){
                let checkedCount = value.length;
                this.checkAll = checkedCount === this.tableLabel.length;
                this.isIndeterminate = checkedCount > 0 && checkedCount < this.tableLabel.length;
                value.forEach(v =>{
                    this.tableLabel.forEach(e =>{
                        if(v == e.param){
                            this.checkedList.push(e.param)
                            this.headerData.push(e)
                        }
                    })
                })
            }
            console.log('Select one',value)
            this.$store.commit('pdfOperate',{"name":this.$parent.title, "type":"table", "data":this.selectedData, "head":this.headerData})
            this.$emit('changeHeader', this.headerData)
        },
        handleSelectionChangeMultiple(value,name,header){
            this.selectedData = value
            this.$store.commit('pdfOperate',{"name":name, "type":"table", "data":this.selectedData, "head":header})
        },
        handleSelectionChange(value){
            console.log(value)
            this.selectedData = value
            this.$store.commit('pdfOperate',{"name":this.$parent.title, "type":"table", "data":this.selectedData, "head":this.headerData})
        },

        createradarEcharts:function(id, _title, _legend, _radar, _series){
            var obj = this
            var mainChart = document.getElementById(id)
            let draw = obj.$echarts.init(mainChart)
            var ele_Resize = elementResize({
              strategy: 'scroll',
              callOnAdd: true
            })
            ele_Resize.listenTo(mainChart, function(element) {
                obj.$echarts.init(mainChart).resize()
                draw.setOption({
                    title: _title,
                    tooltip: {},
                    legend: _legend,
                    radar: _radar,
                    series: _series
                })
            });
        },

        createBarEcharts:function(id, _title, _legend, _xAxis, _yAxis, _series){
            var obj = this
            var mainChart = document.getElementById(id)
            let draw = obj.$echarts.init(mainChart)
            var ele_Resize = elementResize({
              strategy: 'scroll',
              callOnAdd: true
            })
            ele_Resize.listenTo(mainChart, function(element) {
               obj.$echarts.init(mainChart).resize()
               draw.setOption({
                    title: _title,
                    tooltip: {},
                    xAxis: _xAxis,
                    yAxis: _yAxis,
                    legend: _legend,
                    series: _series
                })
            });
        },
        createLineEchartsCommon: function(id, _title, _legend, _xAxis, _yAxis, _series){
            var obj = this
            var mainChart = document.getElementById(id)
            let draw = obj.$echarts.init(mainChart)
            var ele_Resize = elementResize({
              strategy: 'scroll',
              callOnAdd: true
            })
            ele_Resize.listenTo(mainChart, function(element) {
                obj.$echarts.init(mainChart).resize()
                draw.setOption({
                    title: _title,
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'cross',
                            label: {
                                backgroundColor: '#6a7985'
                            }
                        }
                    },
                    legend: _legend,
                    xAxis: _xAxis,
                    yAxis: _yAxis,
                    series: _series
                })
            });
            
        },
        createLineECharts(id, _title, _legend, _xAxis, _yAxis, _series){
            var obj = this
            var mainChart = document.getElementById(id)

            let draw = obj.$echarts.init(mainChart)

            var ele_Resize = elementResize({
              strategy: 'scroll',
              callOnAdd: true
            })
            ele_Resize.listenTo(mainChart, function(element) {
               obj.$echarts.init(mainChart).resize()
               draw.setOption({
                    // title: { text: _title, left: 'center', align: 'right', top: 35 },
                    title: _title,
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'cross',
                            label: {
                                backgroundColor: '#6a7985'
                            }
                        }
                    },
                    legend: _legend,
                    grid: { top : '20%', left: '3%', right: '4%', containLabel: true },
                    xAxis: [{type: 'category', boundaryGap: false, data: _xAxis}],
                    yAxis: _yAxis,
                    series: _series
                })
            });
            
        },
        getPdf_no_page(){
            var day = new Date();
            var strData = day.getFullYear()+"-" + (day.getMonth()+1) + "-" + day.getDate();
            var title = 'pdf_'+strData
            var canvas2 = document.createElement("canvas");
            let _canvas = document.querySelector('#printPage');
            var w = document.querySelector('#printPage').scrollWidth
            var h = document.querySelector('#printPage').scrollHeight
            canvas2.width = w * 2;
            canvas2.height = h * 2;
            canvas2.style.width = w + "px";
            canvas2.style.height = h + "px";
            canvas2.useCORS= true;
            canvas2.allowTaint =false;

            var context = canvas2.getContext("2d")
            context.scale(2,2);
            html2Canvas(document.querySelector('#printPage'),{canvas:canvas2}).then(function(canvas) {            
            var pdf = new JsPDF('p', 'mm', 'a4');
            var ctx = canvas.getContext('2d'), a4w = 190, a4h = 277,
                imgHeight = Math.floor(a4h * canvas.width / a4w),
                renderedHeight = 0;
            while(renderedHeight < canvas.height) {
                var page = document.createElement("canvas");
                page.width = canvas.width;
                page.height = Math.min(imgHeight, canvas.height - renderedHeight);

                page.getContext('2d').putImageData(ctx.getImageData(0, renderedHeight, canvas.width, Math.min(imgHeight, canvas.height - renderedHeight)), 0, 0);
                pdf.addImage(page.toDataURL('image/jpeg', 1.0), 'JPEG', 10, 10, a4w, Math.min(a4h, a4w * page.height / page.width));
                renderedHeight += imgHeight;
                if(renderedHeight < canvas.height)
                    pdf.addPage();
            }

            pdf.save(title + '.pdf')

            });
        },
        getPdf_page(){
            var day = new Date();
            var strData = day.getFullYear()+"-" + (day.getMonth()+1) + "-" + day.getDate();
            var title = 'pdf_'+strData
            var canvas2 = document.createElement("canvas");
            let _canvas = document.querySelector('#printPage');
            var w = document.querySelector('#printPage').scrollWidth
            var h = document.querySelector('#printPage').scrollHeight
            // var w = parseInt(window.getComputedStyle(_canvas).width);
            // var h = parseInt(window.getComputedStyle(_canvas).height);

            canvas2.width = w * 2;
            canvas2.height = h * 2;
            canvas2.style.width = w + "px";
            canvas2.style.height = h + "px";
            canvas2.useCORS= true;
            canvas2.allowTaint =false;

            var context = canvas2.getContext("2d")
            context.scale(2,2);
            html2Canvas(document.querySelector('#printPage'),{canvas:canvas2}).then(function(canvas) {            
                    // document.body.appendChild(canvas)
                // let contentWidth = canvas.width
                // let contentHeight = canvas.height
                // let pageHeight = contentWidth / 592.28 * 841.89
                // let leftHeight = contentHeight
                // let position = 10
                // let imgWidth = 575.28
                // let imgHeight = 592.28 / contentWidth * contentHeight
                // let pageData = canvas.toDataURL('image/jpeg', 1.0)
                // // let PDF = new JsPDF('', 'pt', 'a4')
                // let PDF = new JsPDF('p', 'mm', 'a4')
                // if (leftHeight < pageHeight) {
                //     PDF.addImage(pageData, 'JPEG', 10, 10, imgWidth, imgHeight)
                // } else {
                //     while (leftHeight > 0) {
                //         PDF.addImage(pageData, 'JPEG', 10, position, imgWidth, imgHeight)
                //         leftHeight -= pageHeight
                //         position -= 841.89
                //         if (leftHeight > 0) {
                //             PDF.addPage()
                //         }
                //     }
                // }
            var pdf = new JsPDF('p', 'mm', 'A4');
            //a4w = 190, a4h = 277
            var ctx = canvas.getContext('2d'), a4w = 190, a4h = 277,
                imgHeight = Math.floor(a4h * canvas.width / a4w),
                renderedHeight = 0;
            while(renderedHeight < canvas.height) {
                var page = document.createElement("canvas");
                page.width = canvas.width;
                page.height = Math.min(imgHeight, canvas.height - renderedHeight);

                page.getContext('2d').putImageData(ctx.getImageData(0, renderedHeight, canvas.width, Math.min(imgHeight, canvas.height - renderedHeight)), 0, 0);
                pdf.addImage(page.toDataURL('image/jpeg', 1.0), 'JPEG', 10, 10, a4w, Math.min(a4h, a4w * page.height / page.width));    //添加图像到页面，保留10mm边距
                renderedHeight += imgHeight;
                if(renderedHeight < canvas.height)
                    pdf.addPage();
            }

            pdf.save(title + '.pdf')

            });

        },
        getPdf1(){
            var day = new Date();
            var strData = day.getFullYear()+"-" + (day.getMonth()+1) + "-" + day.getDate();
            var title = 'pdf_'+strData
            console.log(document.querySelector('#printPage').scrollHeight)
            html2Canvas(document.querySelector('#printPage'), {
                useCORS: true,
                width: window.screen.availWidth,
                height: document.querySelector('#printPage').scrollHeight+100,
                windowWidth: document.body.scrollWidth,
                windowHeight: document.querySelector('#printPage').scrollHeight+100,
                x:0,
                // y:window.pageYOffset
                y:0
            }).then(function(canvas) {
                document.body.appendChild(canvas)
                // let contentWidth = canvas.width
                // let contentHeight = canvas.height
                // let pageHeight = contentWidth / 592.28 * 841.89
                // let leftHeight = contentHeight
                // let position = 50
                // let imgWidth = 575.28
                // let imgHeight = 592.28 / contentWidth * contentHeight
                // let pageData = canvas.toDataURL('image/jpeg', 1.0)
                // let PDF = new JsPDF('', 'pt', 'a4')
                // if (leftHeight < pageHeight) {
                //     console.log('')
                //     PDF.addImage(pageData, 'JPEG', 10, 10, imgWidth, imgHeight)
                // } else {
                //     console.log('')
                //     while (leftHeight > 0) {
                //         PDF.addImage(pageData, 'JPEG', 10, position, imgWidth, imgHeight)
                //         leftHeight -= pageHeight
                //         position -= 841.89
                //         if (leftHeight > 0) {
                //             PDF.addPage()
                //         }
                //     }
                // }
                // PDF.save(title + '.pdf')
            });
    },
    }
  }
</script>
