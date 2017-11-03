
function log(){
	setTimeout(function timeout() {
		console.log("next");
		log();
	}, 5000);
}

log();
