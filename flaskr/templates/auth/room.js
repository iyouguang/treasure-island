function room()
{
$(document).ready(function() {
	var playerid=0;
	var roomid=0;
	var socket = io.connect('http://127.0.0.1:5000');

	socket.on('connect',function(){ //连接上后发送playerid,roomid给服务器
		socket.send($('playerid'));
		socket.send($('roomid'));
	});


	socket.on('membership',function(msg){//刷新房间状态
		if(msg)
		{
			$("#ready").append("Start");
		}
		else
		{
			$("#ready").append("Ready");
		}
	});

	$('#refresh').on('click',function(){ //刷新房间状态
		socket.send("Refresh Room!");
		socket.on('roomnum',function(msg){
			$("#room_num").val();
			$("#room_num").append("online players:");
			$("#room_num").append(msg);
		});
		socket.on('roommember',function(msg){
			$("#room_member").val();
			for(member in msg)
			{
				$("#room_member").append('<li>'+member+'</li>');
			}
		})
	});

	$('#ready').on('click',function(){  //发送准备状态
		socket.send("Player is ready!");
	});
	$('#leave').on('click',function(){  //发送离开房间请求
		socket.send("Player is leaving!");
	});

	


});
}


