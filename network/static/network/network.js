document.addEventListener('DOMContentLoaded', function() {

document.querySelectorAll('#like').forEach(item => {
    item.addEventListener('click', addlike)
  })

document.querySelectorAll('#unlike').forEach(item => {
    item.addEventListener('click', removelike)
  })
});   

function addlike() {
    let post_id=this.value;
    fetch('/like/'+post_id,{method:'POST'}).then(response=>response.json()
        ).then(res=>{
            document.querySelector(`._${post_id}`).innerHTML=res.likes;
            document.querySelector(`.like${post_id}`).style.display='none';
            document.querySelector(`.unlike${post_id}`).style.display='block';
        });
}

function removelike() {
    let post_id=this.value;
    fetch('/like/'+post_id,{method:'PUT'}).then(response=>response.json()
        ).then(res=>{
            document.querySelector(`._${post_id}`).innerHTML=res.likes;
            document.querySelector(`.like${post_id}`).style.display='block';
            document.querySelector(`.unlike${post_id}`).style.display='none';
            
        });
}