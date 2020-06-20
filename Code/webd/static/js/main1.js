
$(function(){
	var container = document.getElementById('mynetwork2');
	
	var i;
	$.get('/output1', function(result) {
container.innerHTML="";
		if (result=="this is not apt"){container.innerHTML+=("<h2>这不是apt</h2>");}
		else{
			if(result[0]==1){container.innerHTML+=(JSON.stringify(result[1]));}
			else{
				container.innerHTML+=("<h2>这是apt\n</h2>");
				container.innerHTML+=("<h2>其属于各家族的概率\n</h2>");
				for (i in result){
					container.innerHTML+=(JSON.stringify(i));
					container.innerHTML+=(":");
					container.innerHTML+=(JSON.stringify(result[i]));
					container.innerHTML+=("\n");
						};
				}
  		}
});
  });
