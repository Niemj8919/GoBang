
$(function(){
	var container = document.getElementById('mainchart2');
	var myChart2 = echarts.init(container);
	myChart2.showLoading();
	$.get('/graph1', function(result) {
		myChart2.hideLoading();
	var categorynum=[];
		var i=0;
	  var categories = [];
	  var catedata=[];
var cateid=[];
	  //var allNodes;
	  //allNodes = arrayToObject(result.nodes);
	  result.nodes.forEach(function (node) {
		node.itemStyle = null;
		if (cateid.indexOf(node.name)>-1){
			categorynum[cateid.indexOf(node.name)]=categorynum[cateid.indexOf(node.name)]+1
		}
		else{
        categories.push({
            name: node.name
		});
		cateid[i]=node.name;
		categorynum[i]=1;
		i=i+1;
		}
		node.category = node.name;
	  });
	  for (j=0;j<i;j=j+1){
		  catedata.push({value:categorynum[j],
			name:cateid[j]
		})
	  }
		option = {
			title: {
				text: 'family numbers',
				top: 'bottom',
				left: 'right'
			},
			legend: [{
				data: categories.map(function (a) {
					return a.name;
				})
			}],
			tooltip: {
				trigger: 'item',
				formatter: '{a} <br/>{b}: {c} ({d}%)'
			},
			series: [
				{
					labelLine: {
						show: false
					},	
					avoidLabelOverlap: false,
					name: 'family numbers',
					type: 'pie',
					radius: ['50%', '70%'],
					emphasis: {
						label: {
							show: true,
							fontSize: '30',
							fontWeight: 'bold'
						}
					},
					itemStyle:{
						normal:{
							color: function(params) {
								// build a color map as your need.
								var colorList = [
								  '#C1232B','#B5C334','#FCCE10','#E87C25','#27727B',
								   '#FE8463','#9BCA63','#FAD860','#F3A43B','#60C0DD',
								   '#D7504B','#C6E579','#F4E001','#F0805A','#26C0C0'
								];
								return colorList[params.dataIndex]
							},
						}
					},
					data: catedata,
					label: {
						show: false,
						position: 'center'
					},
				}
			]
		};
	myChart2.setOption(option);
  }, 'json');
  });
