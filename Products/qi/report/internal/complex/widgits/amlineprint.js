
var registeredwidgits=new Array();
var foundwidgits=new Array();
function amChartInited(chartid)
{
    registeredwidgits[registeredwidgits.length]=chartid;
}
started=false
function doprint()
{
    //disable the print button
    started=true
    document.getElementById("printbutton").disabled=true;
    //put up please wait 
    document.getElementById("waitdiv").style.display="Block";
    document.getElementById("percentdone").innerHTML="0";
    for(i=0; i <registeredwidgits.length;i++)
    {
        widgitname=registeredwidgits[i];
        cachewidgit(widgitname);
        
    }
    foundwidgits=new Array();
    if (registeredwidgits.length==0)
    {
        finalPrint();
    }
}

function cachewidgit(widgitname)
{
    widgit=document.getElementById(widgitname);
    widgit.exportImage();
}


function finalPrint()
{
    for (i =0; i < foundwidgits.length;i++)
    {
        chartid=foundwidgits[i];
        //chartobject=document.getElementById(chartid);
        //eliminate the chart- and the :flash for the juicy bit
        middlepart=chartid.substring(6, chartid.length-6);
        imgid="chart-"+middlepart+":image";
        wrapperid="chart-"+middlepart;
        chartobject=document.getElementById(wrapperid);
        imgurl=middlepart+"/cached.png";
        imgtag=document.getElementById(imgid);
        imgtag.src=imgurl;
        //alert(imgtag)
        //alert(imgurl)
        imgtag.style.display="block";
        chartobject.style.display="None";
    }
    document.getElementById("waitdiv").style.display="none";

    window.print();
    for (i =0; i < foundwidgits.length;i++)
    {
        chartid=foundwidgits[i];
        middlepart=chartid.substring(6, chartid.length-6);
        wrapperid="chart-"+middlepart;
        chartobject=document.getElementById(wrapperid);
        chartobject.style.display="inline";

        imgid="chart-"+middlepart+":image";
        imgtag=document.getElementById(imgid)
        imgtag.style.display="None";
    }
    started=false
    document.getElementById("printbutton").disabled=false;
}

function amReturnImageData(chart_id, data)
{
    //alert("woo chaching "+chart_id);
    if(started)
    {
        foundwidgits.push(chart_id);
        document.getElementById("percentdone").innerHTML=(100*foundwidgits.length/registeredwidgits.length).toString();
        if (foundwidgits.length==registeredwidgits.length)
        {
            setTimeout("finalPrint()",2000)
        }
    }
}


function dir(object)
{
    methods = [];
    for (z in object) if (typeof(z) != 'number') methods.push(z);
    return methods.join(', ');
}