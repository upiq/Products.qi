function addattachment()
{
    addedto=document.getElementById("attachments");
    addedElement=document.createElement("div");
    addedElement.innerHTML="<input type=\"file\" style=\"width:300px;\" name=\"attachment\"/>"
    addedto.appendChild(addedElement)
    //TODO: add some boring DOM trickery
}