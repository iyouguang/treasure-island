funtion room()
{
	$(document).ready(function(){
	var playerid = 0;
	var selection = 0;

	var socket = io.connect('http://127.0.0.1:5000');

	socket.on('connect',function(){ //连接上后发送playerid给服务器
	    socket.send($('playerid'));
	});

	socket.on('grade',function(msg){ //接受服务器所发来的当前分数
        $("#grade").append(msg)
	});

	socket.on('rank',function(msg){ //接受服务器所发来的当前排名
        $("#rank").append(msg)
	});



	});
}