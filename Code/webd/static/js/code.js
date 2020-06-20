
$(function(){
	var container = document.getElementById('mynetwork');
	var myChart = echarts.init(container);
	myChart.showLoading();
	$.get('/graph', function(result) {
		myChart.hideLoading();
        var edgee=[];
        var cateid=[];
        var lineee=[];
        var maxxx=0;
        var categorynum=[];
		var i=0;
                var j=0;
	  var categories = [];
	  //var allNodes;
	  //allNodes = arrayToObject(result.nodes);
	  result.nodes.forEach(function (node) {
        node.itemStyle = null;
        /*categories.push({
            name: node.name
        });*/
		node.category = node.name;
		if (categorynum.indexOf(node.category)>-1){
               node.categorynum=categorynum.indexOf(node.category);
               cateid[node.categorynum]=cateid[node.categorynum]+1;
               node.cateid=cateid[categorynum.indexOf(node.category)]; 
              }
                else{
              
              categorynum.push(node.category);
              node.categorynum=j;
              cateid[j]=1;
              j=j+1;
              node.cateid=1;
             }
if (node.ttype=='new'){
node.category=node.ttype;
categories.push({
            name: node.ttype
        });
}
else{
            categories.push({
            name: node.name
        })};
	  });
result.nodes.forEach(function (node) {
             node.x=Math.cos(2*(node.cateid / cateid[node.categorynum])*(Math.PI))*cateid[node.categorynum]*24+Math.cos(2*(node.categorynum/categorynum.length)*(Math.PI))*14000;
             node.y=Math.sin(2*(node.cateid / cateid[node.categorynum])*(Math.PI))*cateid[node.categorynum]*24+Math.sin(2*(node.categorynum/categorynum.length)*(Math.PI))*14000;
});
result.nodes.forEach(function (node){
if (node.ttype=='new'){
node.itemStyle=[]
node.itemStyle.push({color:'rgba(0,0,0,1)'});
}
});
             for (i=0;i<categorynum.length;i++){
                result.nodes.push({
		     id:1000000+i,
                     name:1000000+i,
                     x:Math.cos(2*(i/categorynum.length)*(Math.PI))*14000,
                     y:Math.sin(2*(i/categorynum.length)*(Math.PI))*14000,
                     symbolSize:cateid[i],
                     itemStyle: {
                            color:'rgba(128,128,128,0.5)'
                        },
		     fam:categorynum[i],
                    label:{
                formatter:categorynum[i],
                show:true,
                color:'rgba(0,0,0,1)'
                          }
                   })
};
for (i=0;i<(categorynum.length*categorynum.length);i++)
{lineee[i]=0;}
result.edges.forEach(function (edge) {

if (edge.sname==edge.tname){
edgee.push(edge);
}
else{
lineee[categorynum.indexOf(edge.sname)*categorynum.length+categorynum.indexOf(edge.tname)]+=edge.width;
}
});
for (i=0;i<(categorynum.length*categorynum.length);i++)
{
if (lineee[i]>0){

lineee[i]=lineee[i]/250+1;
if (lineee[i]>10){lineee[i]=10}
edgee.push({
widdth:lineee[i],
source:(1000000+Math.floor(i/categorynum.length))+'',
target:(1000000+i%categorynum.length)+'',
lineStyle:{width:lineee[i],
color:'rgba(0,0,0,1)'
}
});
}
}
const arrayToObject = (array) =>
    array.reduce((obj, item) => {
        obj[item.id] = item
        return obj
    }, {});
allNodes = arrayToObject(result.nodes);
		option = {
                        color:[ 
                               '#C1232B','#B5C334','#FCCE10','#E87C25','#27727B',
                               '#FE8463','#9BCA63','#FAD860','#F3A43B','#60C0DD',
                               '#D7504B','#C6E579','#F4E001','#F0805A','#26C0C0',
                               '#c23531','#2f4554','#61a0a8','#d48265','#91c7ae',
                               '#749f83','#ca8622','#bda29a','#6e7074','#546570', '#c4ccd3'
                            ],
			title: {
				text: 'APT gene map',
				subtext: 'Circular layout',
				top: 'bottom',
				left: 'right'
			},
			tooltip: {
			formatter: function (params) {
var res;
                		if (params.dataType == "node") {
                    			var colorSpan = color => '<span style="display:inline-block;margin-left:5px;border-radius:10px;width:9px;height:9px;background-color:' + color + '"></span>';
                    // is node
                    			res = "<b>Family</b>: " + params.data.fam + colorSpan(params.color);
                		} else if (params.dataType == "edge") {
                    // is edge
                    	res = "<b>relationship</b>: "+allNodes[params.data.source].fam + " > " + allNodes[params.data.target].fam+"<br><b>degree of relationship</b>: "+params.data.widdth;
                }
                return res;
            }


			},
			legend: [{
				data: categories.map(function (a) {
					return a.name;
				})
			}],
			animationDurationUpdate: 1500,
			animationEasingUpdate: 'quinticInOut',
			series: [{
					name: 'apt map',
					type: 'graph',
					layout: 'none',
                                        symbolSize:3,
					data: result.nodes,
					links: edgee,
					categories: categories,
					roam: true,
					label: {
						position: 'right',
						formatter: '{b}'
					},
					lineStyle: {
						color: 'source',
						curveness:0,
					}
				}
			]
		};
	myChart.setOption(option);
  }, 'json');
  });
