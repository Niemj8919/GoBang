
$(function(){
	var container = document.getElementById('mainchart3');
	var myChart3= echarts.init(container);
	myChart3.showLoading();
	$.get('/graph2', function(result) {
		myChart3.hideLoading();
	var categorynum=[];
		var i=0;
	  var categories = [];
	  var catedata=[];
var cateid=[];
	  //var allNodes;
	  //allNodes = arrayToObject(result.nodes);
	  result.nodes.forEach(function (node) {
		node.itemStyle = null;
node.name=node.ttype;
		if (cateid.indexOf(node.ttype)>-1){
			categorynum[cateid.indexOf(node.ttype)]=categorynum[cateid.indexOf(node.ttype)]+1
		}
		else{
        categories.push({
            name: node.ttype
		});
		cateid[i]=node.ttype;
		categorynum[i]=1;
		i=i+1;
		}
		node.category = node.ttype;
	  });
	  for (j=0;j<i;j=j+1){
		  catedata.push({value:categorynum[j],
			name:cateid[j]
		})
	  }
		option = {
			title: {
				text: 'amount of new/old apts',
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
	myChart3.setOption(option);
  }, 'json');
  });
