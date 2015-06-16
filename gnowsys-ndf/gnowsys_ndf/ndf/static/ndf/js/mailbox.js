// The Global variables
var Readstart;
var Unreadstart;
var typeOfMail; // 0 for the unread ones and 1 for the read ones
var mailbox_name;
var userName;
var CSRFtoken;
function countInitialize(){
	Readstart = 0;
	Unreadstart = 0;
	typeOfMail = 0;
}

function increaseMailFetchCount(){
	if (typeOfMail == 0){
		Unreadstart = Unreadstart + 50;
	}
	else{
		Readstart = Readstart + 50;
	}
	alert('Unread: ' + Unreadstart + ' Read: ' + Readstart);
	getMails();
}


function decreaseMailFetchCount(){
	if (typeOfMail == 0){
		Unreadstart = Unreadstart - 50;
		if(Unreadstart < 0){
			Unreadstart = 0;
		}
	}
	else {
		Readstart = Readstart - 50;
		if(Readstart < 0) { 
			Readstart = 0;
		}
	}
	alert('Unread: ' + Unreadstart + ' Read: ' + Readstart);
	getMails();

}


function getMails(){
	var temp = 0;
	if(typeOfMail == 0){
		temp = Unreadstart;
	}
	else {
		temp = Readstart;
	}
	$.post( 'mailresponse/', {'mailBoxName':mailbox_name, 'username': userName, 'csrfmiddlewaretoken': CSRFtoken, 'mail_type': typeOfMail, 'startFrom': temp}, function(data){		
		var content = $(data).filter( '#mailContent' );
		$( ".mailBoxContent" ).empty().append( content );
	});
}


// Function to put a POST request to fetch mails
function setMailBoxName(username, csrf_token, mailBoxName) {
	document.getElementById( 'mailBoxName' ).innerHTML = mailBoxName;
	/*code to set the 'mailbox_settings' url*/
	set_link=$("#set_box").attr("href");
	set_link=set_link.replace('dummy',mailBoxName);
	$("#set_box").attr("href", set_link);

	/*code to set the 'compose_mail' url*/
	new_mail_link=$("#compose_mail").attr("href");
	new_mail_link=new_mail_link.replace('dummy',mailBoxName);
	$("#compose_mail").attr("href", new_mail_link);

	mailbox_name = mailBoxName;
	userName = username;
	CSRFtoken = csrf_token;
	countInitialize();
	getMails();

	a=$("#set_box").attr("href");
	a=a.replace('dummy',mailBoxName);
	$("#set_box").attr("href", a);

}

$(document).ready(function(){
	$("#unreadMailsLink").click(function(){
		Unreadstart = 0;
		typeOfMail = 0;
		getMails();
	});

	$("#readMailsLink").click(function(){
		Readstart = 0;
		typeOfMail = 1;
		getMails();
	});
});



