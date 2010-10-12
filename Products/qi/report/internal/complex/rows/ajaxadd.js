function connect()
{
    if (window.XMLHttpRequest)
    {
        // code for IE7+, Firefox, Chrome, Opera, Safari
        return new XMLHttpRequest();
    }
    if (window.ActiveXObject)
    {
        // code for IE6, IE5
        return new ActiveXObject("Microsoft.XMLHTTP");
    }
    return null;
}

function showaddscreen()
{
    
    addregion=document.getElementById('addregion')
    addregion.style.display="Block"
}

function cancelscreen()
{
    addregion=document.getElementById('addregion')
    addregion.style.display="None"
}
var client=null;
function ajaxstep(args)
{
    if(client.readyState==4 && client.status==200)
    {
        
        responsexml=client.responseXML
        responsetext=client.responseText
        replacedid=document.getElementById("modifiedrow").value
        replaced=document.getElementById(replacedid)
        newpart="<span id=\""+replacedid+"\" ></div>"
        replaced.id='newlyadded'
        replaced.innerHTML="<span class=\"widgitgroup design\">"+responsetext+"</span>"+newpart
    }
}

function processchange(rowid,url, type)
{
    client= connect();
    ajaxurl=url+"?add=added&type="+type
    client.open("GET",ajaxurl,true);
    client.onreadystatechange=ajaxstep;
    client.send(null);
}

function submitscreen()
{
    row=document.getElementById("modifiedrow").value
    type=document.getElementById("addedtype").value
    url=document.getElementById("rowurl").value
    processchange(row,url,type)
    addregion=document.getElementById('addregion')
    addregion.style.display="None"
}

function doadd(rowid, rowurl)
{
    addedrow=document.getElementById("modifiedrow")
    addedrow.value=rowid
    addedurl=document.getElementById("rowurl")
    addedurl.value=rowurl
    showaddscreen()
}