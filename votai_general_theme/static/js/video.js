(function() {
	
	var streaming 		= false,
		video 			= document.querySelector('#video'),
		canvas			= document.querySelector('#canvas'),
		photo			= document.querySelector('#soulmate-pic'),
		startbutton		= document.querySelector('.button_pic'),
		resetbutton  	= document.querySelector('#resetbutton'),
		uploadbutton 	= document.querySelector('#uploadbutton'),
		width 			= 640,
		height 			= 450;

	function init() {
		navigator.getMedia = 	navigator.getUserMedia ||
								navigator.webkitGetUserMedia ||
								navigator.mozGetUserMedia;

		navigator.getMedia(
			{
				video: true,
				audio: false
			},
			function(stream) {
				window.stream = stream; // stream available to console
				if (navigator.mozGetUserMedia) {
					video.mozSrcObject = stream;
				} else {
					var vendorURL = window.URL || window.webkitURL;
					video.src = vendorURL ? vendorURL.createObjectURL(stream) : stream;
				}
				video.play();
			},
			function(err) {
				console.log("An error occured! " + err);
			}
		);
	};

	video.addEventListener('canplay', function(ev)
	{
		if (!streaming) {
			//height = video.videoHeight / (video.videoWidth/width);
			
			video.setAttribute('width', width);
			video.setAttribute('height', height);
			canvas.setAttribute('width', width);
			canvas.setAttribute('height', height);
			streaming = true;
		}
	}, false);

	function takepicture() {
		context = canvas.getContext('2d');

		canvas.width = width;
		canvas.height = height;
		context.drawImage(video, 0, 0, width, height);

		var img = new Image();
		img.src = photo.getAttribute("src");
		context.drawImage(img, 0, 0, 320, 450);

		//play with DOM
		document.getElementById('videocontainer').setAttribute('style','display:none');
		document.getElementById('canvas').setAttribute('style','');
		document.getElementById('uploadbutton').setAttribute('style','');
		document.getElementById('takepicbutton').setAttribute('style','display:none');
		// document.getElementById('icon-repeat').classList.add('icon-spin');
		document.getElementById('resetbutton').setAttribute('style','');
	}

	function upload() {

		document.getElementById('resetbutton').setAttribute('style','display:none');
		document.getElementById('uploadbutton').innerHTML = '<i class="icon-gear icon-spin"></i> Cargando';

		var head 	= /^data:image\/(png|jpg);base64,/,
			fd 		= new FormData(),toSend,
			xhr 	= new XMLHttpRequest(),
			links 	= '',
			data 	= '',
			originalImage = '';

		data = ('mozGetAsFile' in canvas) ? canvas.mozGetAsFile('webcam.png') : canvas.toDataURL('image/png').replace(head, '');

		fd.append('image', data);

		xhr.open('POST', 'https://api.imgur.com/3/image');

		xhr.addEventListener('error', function(ev) {
			console.log('Upload Error :'+ev);
		}, false);

		xhr.addEventListener('load', function(ev) {
			try {
				var links = JSON.parse(xhr.responseText).data.link;

				var twtwindow = "https://twitter.com/share?url=http://"+twitter_url+"&text="+candidate_name+"+%3C3+"+links+"&hashtags=medianaranja,votainteligente";
				var fcbkwindow = "https://www.facebook.com/sharer/sharer.php?u="+links;

				document.getElementById('socialsharehalfface').setAttribute('style','');
				document.getElementById('shareurl').setAttribute('value', links);
				document.getElementById('shareurltwitter').setAttribute('onClick','window.open(\''+twtwindow+'\', \'twitter-share-dialog\', \'width=626,height=436\'); ga(\'send\', \'event\', \'share-halfface-twitter\', \'click\');');
				document.getElementById('shareurlfacebook').setAttribute('onClick','window.open(\''+fcbkwindow+'\', \'twitter-share-dialog\', \'width=626,height=436\'); ga(\'send\', \'event\', \'share-halfface-facebook\', \'click\');');
				document.getElementById('uploadbutton').innerHTML = 'OK';
				document.getElementById('uploadbutton').setAttribute('style','display:none');
				document.getElementById('resetbutton').setAttribute('style','');
			} catch(e) {
				console.log('Upload Error :' + e);
			}
		}, false);

		xhr.setRequestHeader('Authorization', "Client-ID " + API_KEY);
		xhr.send(fd);
	}

	/*Event handlers*/

	startbutton.addEventListener('mouseover', function() {
		document.getElementById('apoya').setAttribute('style','display:block');
	}, false);

	startbutton.addEventListener('mouseout', function() {
		document.getElementById('apoya').setAttribute('style','display:none');
	}, false);

	startbutton.addEventListener('click', function(ev){
		init();
		ev.preventDefault();
	}, false);

	takepicbutton.addEventListener('click', function(ev) {
		ev.preventDefault();
		takepicture();
	}, false);

	resetbutton.addEventListener('click', function(ev){
		ev.preventDefault();
		document.getElementById('videocontainer').setAttribute('style','');
		document.getElementById('canvas').setAttribute('style','display:none');
		document.getElementById('uploadbutton').setAttribute('style','display:none');
		document.getElementById('takepicbutton').setAttribute('style','');
		document.getElementById('icon-repeat').classList.remove('icon-spin');
		document.getElementById('resetbutton').setAttribute('style','display:none');
		document.getElementById('socialsharehalfface').setAttribute('style','display:none');
	}, false);

	uploadbutton.addEventListener('click', function(ev){
		ev.preventDefault();
		upload();
	}, false);

})();