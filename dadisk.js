function do_post(action, target)
{
  var xhr = new XMLHttpRequest();
  var data = new FormData();
  var target_div = document.getElementById('status');
  data.append('target', target);
  data.append('action', action);
  xhr.open("POST", "#", false);
  xhr.send(data);
  target_div.innerHTML = '<pre>' + xhr.responseText + '</pre>';
}

function toggle_subs()     { do_post('toggle_subs', null); }
function toggle_play()     { do_post('toggle_play', null); }
function play_file(target) { do_post('play', target) }
function enqueue_file(target) { do_post('enqueue', target) }

