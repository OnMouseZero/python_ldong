    //点击显示弹窗
function showLayer() {
    document.getElementById('layer').style.display='block';
}
    //点击关闭弹窗
function closeLayer() {
    document.getElementById('layer').style.display='none';
    }
    //点击保存并关闭弹窗
function save() {
    var text=document.getElementById('inputText').value;
    listArr.push(text);
    list();
    document.getElementById('layer').style.display='none';
}
