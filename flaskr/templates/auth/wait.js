function wait()
{
$(document).ready(function() {
	var playerid=0;
	var socket = io.connect('http://127.0.0.1:5000');

	socket.on('connect',function(){ //连接上后发送playerid给服务器
		socket.send($('playerid'));
	});

	socket.on('playname',function(msg){//接受服务器发来的玩家昵称信息
		$("#playername").append(msg);
	});

	socket.on('playsocle',function(msg){//接受服务器发来的玩家分数信息
		$("#playersocle").append(msg);
	});

	socket.on('playrecord',function(msg){//接受服务器发来的玩家历史战绩
		for(piece in msg)
		{
			$("#record").append('<li>'+piece+'</li>');
		}
	});

	$('#createroom').on('click',function(){ //创建房间
		socket.send("Create Room!");
	});

	$('#joinroom').on('click',function(){  //发送给服务器房间号以加入房间
		socket.send($('roomid').val());
	});

	


});
}
