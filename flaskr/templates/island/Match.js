funtion room()
{
	$(document).ready(function(){
	var playerid = 0;
	var selection = 0;

	var socket = io.connect('http://127.0.0.1:5000');

	socket.on('connect',function(){ //连接上后发送playerid给服务器
	    socket.send($('playerid'));
	});

	socket.on('question',function(msg){ //接受服务器发来的一道随机题目 匹配失败则无法获得题目
        $("#question").append(msg)
	});

	socket.on('question',function(){ //接受题目后发送自己所选的选项给服务器
        socket.send($('selection'));
	});

	socket.on('result',function(msg){ //接受服务器所发来的结果 同时服务器刷新地图
        $("#result").append(msg)
	});



	});
}