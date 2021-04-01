var files = [];
$(document).ready( function() {

    $(document).on('change', '.btn-file :file', function() {
        var input = $(this),
        label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
        input.trigger('fileselect', [label]);
    });

    $('.btn-file :file').on('fileselect', function(event, label) {

        var input = $(this).parents('.input-group').find(':text'),
        log = label;

        if( input.length ) {
            input.val(log);
        } else {
            if( log ) alert(log);
        }

    });

    $('#use_zoom').change(function() {
        if ($('#use_zoom').is(':checked')) {

            wheelzoom(document.querySelector("#img_upload"), {zoom: 0.1, maxZoom: 10});
        }else{
            document.querySelector('#img_upload').dispatchEvent(new CustomEvent('wheelzoom.destroy'));
        }});

    $('input[type=file]').change(function () {
        console.log(this.files[0].mozFullPath);
        files = this.files
        });

    $('input[type=file]').change(function () {
        console.log(this.files[0].mozFullPath);
        files = this.files
        });

    //Botones para procesar las imagenes con el modelo entrenado

    function cleantables()
    {
        $('#file_data').children('tr').remove();
        $('#med_data').children('tr').remove();

    }
    function processdata(d){

    var json = JSON.parse(d)


    for (key in json.generic){
        $('#file_data').append('<tr><td>'+key+'</td><td>'+json.generic[key]+'</td></tr>')
    }

    for (key in json.med){
        $('#med_data').append('<tr><td>'+key+'</td><td>'+json.med[key]+'</td></tr>')
    }

    if (json.url!=null){

        $('#img_upload').attr('src', json.url['base64']);
    }else
    {
        $('#img_upload').attr('src', '/static/img/dot.gif');
        $('#modal_dialog').modal('toggle');

    }
}
    function processdataStress(d){

    var json = JSON.parse(d)


    for (key in json.generic){
        $('#file_data').append('<tr><td>'+key+'</td><td>'+json.generic[key]+'</td></tr>')
    }

    for (key in json.med){
        $('#med_data').append('<tr><td>'+key+'</td><td>'+json.med[key]+'</td></tr>')
    }

    if (json.url!=null){

        $('#img_uploadStress').attr('src', json.url['base64']);
    }else
    {
        $('#img_uploadStress').attr('src', '/static/img/dot.gif');
        $('#modal_dialog').modal('toggle');

    }
}

        $("#imgInp").change(function(){
            cleantables()

            var formData = new FormData(document.getElementById("form_one"));
            for (var i = 0; i < files.length; i++) {
 
                formData.append("files", files[i]);
                formData.append("paths", files[i]['webkitRelativePath']);
    
             }
            console.log(files[2]['webkitRelativePath']);
            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                processdata(this.responseText);
            }
            };

            xhr.open('POST', 'processRest.ajax', true);
            xhr.send(formData);

        });

    $("#imgInpStress").change(function(){
        cleantables()

        var formData = new FormData(document.getElementById("form_one"));
        for (var i = 0; i < files.length; i++) {
 
            formData.append("files", files[i]);
            formData.append("paths", files[i]['webkitRelativePath']);

         }
        console.log(files[2]['webkitRelativePath']);
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            processdataStress(this.responseText);
        }
        };

        xhr.open('POST', 'processStress.ajax', true);
        xhr.send(formData);
    });


    // Botones dE Zonas de interes para los graficos
    var zona;

    function graphicsdata(tabla){
        var json = JSON.parse(tabla)

        $('#area_rest').html("")
        $('#area_stress').html("")
        $('#res_peak_rest').html("")
        $('#res_peak_stress').html("")
        $('#res_pend_rest').html("")
        $('#res_pend_stress').html("")
        $('#res_ratio_value').html("")
        $('#imgGraphic').html("")

        $('#area_rest').append(json.area_rest)
        $('#area_stress').append(json.area_stress)
        $('#res_peak_rest').append(json.res_peak_rest)
        $('#res_peak_stress').append(json.res_peak_stress)
        $('#res_pend_rest').append(json.res_pend_rest)
        $('#res_pend_stress').append(json.res_pend_stress)
        $('#res_ratio_value').append(json.res_ratio_value)

        if (json.url!=null){
    
            $('#imgGraphic').attr('src', json.url['base64']);
        }else
        {
            $('#imgGraphic').attr('src', '/static/img/dot.gif');    
        }
    }

    
    $("#btnBlood").click(function(){

        var fd = new FormData();
        zona = "1";

        fd.append("zona", zona)
         var xhr = new XMLHttpRequest();
         xhr.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
            graphicsdata(this.responseText);
         }
         };
         xhr.open('POST', 'zona1.ajax', true);
         xhr.send(fd); 
    });
    $("#btnEpi").click(function(){

        var fd = new FormData();

        zona = "2"

        fd.append("zona", zona)
         var xhr = new XMLHttpRequest();
         xhr.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
            graphicsdata(this.responseText);
         }
         };
         xhr.open('POST', 'zona2.ajax', true);
         xhr.send(fd); 
    });
    $("#btnEndo").click(function(){

        var fd = new FormData();

        zona = "3"

        fd.append("zona", zona)
         var xhr = new XMLHttpRequest();
         xhr.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
            graphicsdata(this.responseText);
         }
         };
         xhr.open('POST', 'zona3.ajax', true);
         xhr.send(fd); 
    });


    // Botones dE Zonas de interes para los graficos

    function imagesdata(posImages){
        var json = JSON.parse(posImages)
        $('#img_rest').html("")
        $('#img_stress').html("")
        $('#pos_rest').html("")
        $('#pos_stress').html("")
        $('#pos_rest').append(json.pos_actualRest)
        $('#pos_stress').append(json.pos_actualStress)

        if (json.urlRest!=null || json.urlStress!=null){
    
            $('#img_rest').attr('src', json.urlRest['base64']);
            $('#img_stress').attr('src', json.urlStress['base64']);
        }else
        {
            $('#img_rest').attr('src', '/static/img/dot.gif');   
            $('#img_stress').attr('src', '/static/img/dot.gif');  
        }
    }

    
    $("#btnBloodIma").click(function(){

        var fd = new FormData();

        zona = "1"

        fd.append("zona", zona)
         var xhr = new XMLHttpRequest();
         xhr.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
            imagesdata(this.responseText);
         }
         };
         xhr.open('POST', 'zona1Imagen.ajax', true);
         xhr.send(fd); 
    });
    $("#btnEpiIma").click(function(){

        var fd = new FormData();

        zona = "2"

        fd.append("zona", zona)
         var xhr = new XMLHttpRequest();
         xhr.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
            imagesdata(this.responseText);
         }
         };
         xhr.open('POST', 'zona2Imagen.ajax', true);
         xhr.send(fd); 
    });
    $("#btnEndoIma").click(function(){

        var fd = new FormData();
        zona = "3"
        fd.append("zona", zona)
         var xhr = new XMLHttpRequest();
         xhr.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
            imagesdata(this.responseText);
         }
         };
         xhr.open('POST', 'zona3Imagen.ajax', true);
         xhr.send(fd); 
    });


//Botones para cambiar de imagenes  Rest


function imagesmovedataRest(posRest){
    var json = JSON.parse(posRest)
    $('#img_rest').html("")
    $('#img_stress').html("")
    $('#pos_rest').html("")
    $('#cant_rest').html("")


    $('#pos_rest').append(json.pos_actualRest)
    $('#cant_rest').append(json.cantidad_imgRest)



    if (json.urlRest!=null || json.urlRest!=null){

        $('#img_rest').attr('src', json.urlRest['base64']);
    }else
    {
        $('#img_rest').attr('src', '/static/img/dot.gif');   
    }
}

    $("#btnAtrasRest").click(function(){

        var fd = new FormData();

         var xhr = new XMLHttpRequest();
         xhr.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
            imagesmovedataRest(this.responseText);
         }
         };
         xhr.open('POST', 'movARest.ajax', true);
         xhr.send(fd); 
    });

    $("#btnSigRest").click(function(){

        var fd = new FormData();

         var xhr = new XMLHttpRequest();
         xhr.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
            imagesmovedataRest(this.responseText);
         }
         };
         xhr.open('POST', 'movDRest.ajax', true);
         xhr.send(fd); 
    });


    //Botones para cambiar de imagenes  Rest


function imagesmovedataStress(posStress){
    var json = JSON.parse(posStress)
    $('#img_rest').html("")
    $('#img_stress').html("")
    $('#pos_stress').html("")
    $('#cant_stress').html("")

    $('#pos_stress').append(json.pos_actualStress)
    $('#cant_stress').append(json.cantidad_imgStress)

    if (json.urlStress!=null){

        $('#img_stress').attr('src', json.urlStress['base64']);
    }else
    {   
        $('#img_stress').attr('src', '/static/img/dot.gif');  
    }
}

    $("#btnAtrasStress").click(function(){

        var fd = new FormData();

         var xhr = new XMLHttpRequest();
         xhr.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
            imagesmovedataStress(this.responseText);
         }
         };
         xhr.open('POST', 'movAStress.ajax', true);
         xhr.send(fd); 
    });

    $("#btnSigStress").click(function(){

        var fd = new FormData();

         var xhr = new XMLHttpRequest();
         xhr.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
            imagesmovedataStress(this.responseText);
         }
         };
         xhr.open('POST', 'movDStress.ajax', true);
         xhr.send(fd); 
    });

    // recargar imagen con wl y ww


    $("#btnRecargaIma").click(function(){

        var fd = new FormData();
        var ww = Number(document.getElementById('ww_obt').value);
        var wl = Number(document.getElementById('wl_obt').value);

        fd.append("ww_obt", ww)
        fd.append("wl_obt", wl)

         var xhr = new XMLHttpRequest();
         xhr.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
            imagesdata(this.responseText);
         }
         };
         xhr.open('POST', 'recargar.ajax', true);
         xhr.send(fd); 
    });

    // dividiri miocardio

    var restClick = false;
    var pxRest = 0;
    var pyRest = 0;
    var stressClick = false;
    var pxStress = 0;
    var pyStress = 0;

    var imgR = document.getElementById("img_rest");
    var ctxR = document.getElementById("canvasR").getContext("2d");

    var imgS = document.getElementById("img_stress");
    var ctxS = document.getElementById("canvasS").getContext("2d");
    
    // Canvas Rest
    $("#canvasR").click(function(e){
        getPosition(e); 
        restClick = true;

   });
   
   var pointSize = 3;
   
   function getPosition(event){
        var rect = canvasR.getBoundingClientRect();
        var x = event.clientX - rect.left;
        var y = event.clientY - rect.top;
        
        //alert("eje x:"+x+"eje y:"+y)

        pxRest = x;
        pyRest = y;

        //alert("eje x: "+pxRest+" eje y: "+pyRest)

        drawCoordinates(x,y);
   }
   
   function drawCoordinates(x,y){	
       ctxR.clearRect(0, 0, canvasR.width, canvasR.height);
       ctxR.fillStyle = "#FEFAF9"; // white color
       ctxR.beginPath();
       ctxR.arc(x, y, pointSize, 0, Math.PI * 2, true);
       //ctx.drawImage(img,187,56,278,369,-3,-2,222,295)
       ctxR.drawImage(imgR,187,56,280,372,-2,-2,224,297);
       ctxR.fill();
       
   }

   //Canvas Stress

   $("#canvasS").click(function(e){
    getPositionS(e); 
    stressClick = true;

});

function getPositionS(event){
    var rect = canvasS.getBoundingClientRect();
    var x = event.clientX - rect.left;
    var y = event.clientY - rect.top;
    
    //alert("eje x:"+x+"eje y:"+y)

    pxStress = x;
    pyStress = y;

    //alert("eje x: "+pxRest+" eje y: "+pyRest)

    drawCoordinatesS(x,y);
}

function drawCoordinatesS(x,y){	
   ctxS.clearRect(0, 0, canvasS.width, canvasS.height);
   ctxS.fillStyle = "#FEFAF9"; // white color
   ctxS.beginPath();
   ctxS.arc(x, y, pointSize, 0, Math.PI * 2, true);
   //ctx.drawImage(img,187,56,278,369,-3,-2,222,295)
   ctxS.drawImage(imgS,187,56,280,372,-2,-2,224,297)
   ctxS.fill();
   
}

//Botones para la division




   $("#btnDivMi").click(function(){
    //ctx.drawImage(img,190,58,277,368,220,160,221,294)
    ctxR.drawImage(imgR,187,56,280,372,-2,-2,224,297);
    //ctx.drawImage(img,187,56,278,369,-3,-2,222,295)
    // drawImage(imagen, imgX, imgY, imgAncho, imgAlto, lienzoX, lienzoY, LienzoAncho, LienzoAlto)

    //ctx.drawImage(img,190,58,277,368,220,160,221,294)
    ctxS.drawImage(imgS,187,56,280,372,-2,-2,224,297);

    var x = document.getElementById("myDiv");
    var btnDivMi = document.getElementById("btnDivMi");
    var btnNew = document.getElementById("btnNew");
    
    var img_rest =document.getElementById("img_rest");
    var img_stress=  document.getElementById("img_stress");

    var pointRest=  document.getElementById("pointRest");
    var pointStress=  document.getElementById("pointStress");
    

if (x.style.display === "none") {
    //alert("Aparesco div") Aparece el div
    btnDivMi.style.display = "none";
    btnNew.style.display = "none";
    img_rest.style.display = "none";
    img_stress.style.display = "none";
    //img_stress.style.display = "none";

    pointRest.style.display = "block";
    pointStress.style.display = "block";
    x.style.display = "block";
} else {
    // alert("Desaparesco")
    btnNew.style.display = "none";
    btnDivMi.style.display = "none";
    x.style.display = "none";
}
});

$("#btnCancel").click(function(){
    var x = document.getElementById("myDiv");
    var btnConfirm = document.getElementById("btnComplete");
    var btnDivMi = document.getElementById("btnDivMi");
    var img_rest =document.getElementById("img_rest");
    var img_stress=  document.getElementById("img_stress");

    var pointRest=  document.getElementById("pointRest");
    var pointStress=  document.getElementById("pointStress");
    
if (x.style.display === "none") {
    // alert("Aparesco")
    btnDivMi.style.display = "none";
    x.style.display = "block";
} else {
    // alert("Desaparesco")
    btnDivMi.style.display = "block";
    img_rest.style.display = "block";
    img_stress.style.display = "block";
    
    pointRest.style.display = "none";
    pointStress.style.display = "none"
    x.style.display = "none";
}
});


function imagepartition(partImage){
    var json = JSON.parse(partImage)
    $('#img_rest').html("")
    $('#img_stress').html("")
    $('#pos_rest').html("")
    $('#pos_stress').html("")
    $('#pos_rest').append(json.pos_actualRest)
    $('#pos_stress').append(json.pos_actualStress)

    if (json.urlRest!=null || json.urlStress!=null){

        $('#img_rest').attr('src', json.urlRest['base64']);
        $('#img_stress').attr('src', json.urlStress['base64']);
    }else
    {
        $('#img_rest').attr('src', '/static/img/dot.gif');   
        $('#img_stress').attr('src', '/static/img/dot.gif');  
    }
}

$("#btnConf").click(function(){

    var xRest, yStress;
    var xStress, yStress;


    if(restClick == true && stressClick == true ){

        restClick = false;
        stressClick = false;
        var fd = new FormData();

        xRest = parseInt(pxRest)
        yRest = parseInt(pyRest)

        xStress = parseInt(pxStress)
        yStress = parseInt(pyStress)

        fd.append("xRest", xRest)
        fd.append("yRest", yRest)
        fd.append("xStress", xStress)
        fd.append("yStress", yStress)

        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            imagepartition(this.responseText);
        }
        };
        xhr.open('POST', 'partition.ajax', true);
        xhr.send(fd); 

        var x = document.getElementById("myDiv");
        var cbo = document.getElementById("cboxPartition");
        var btnDivMi = document.getElementById("btnDivMi");

        var img_rest =document.getElementById("img_rest");
        var img_stress=  document.getElementById("img_stress");

        var pointRest=  document.getElementById("pointRest");
        var pointStress=  document.getElementById("pointStress");
        

        if (x.style.display === "none") {
            // alert("Aparesco")
            btnDivMi.style.display = "none";
            x.style.display = "block";
        } else {
            // alert("Desaparesco")
            btnDivMi.style.display = "block";
            img_rest.style.display = "block";
            img_stress.style.display = "block";
            cbo.style.display = "block";
            
            pointRest.style.display = "none";
            pointStress.style.display = "none"
            x.style.display = "none";
        }
    }else{
        alert("No se puede realizar la division, falta seleccionar un punto ")
    }
     
});



function subdivimage(partImage){
    var json = JSON.parse(partImage)
    $('#img_rest').html("")
    $('#img_stress').html("")
    $('#pos_rest').html("")
    $('#pos_stress').html("")
    $('#pos_rest').append(json.pos_actualRest)
    $('#pos_stress').append(json.pos_actualStress)

    if (json.urlRest!=null || json.urlStress!=null){

        $('#img_rest').attr('src', json.urlRest['base64']);
        $('#img_stress').attr('src', json.urlStress['base64']);
    }else
    {
        $('#img_rest').attr('src', '/static/img/dot.gif');   
        $('#img_stress').attr('src', '/static/img/dot.gif');  
    }
}

$('#cboPart').on('change', function()
{
        var fd = new FormData();
        if (zona  == null){
            zona = "1";
        }
        fd.append("zona", zona)
        fd.append("particion", this.value)

        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            subdivimage(this.responseText);
        }
        };
        xhr.open('POST', 'subdiv.ajax', true);
        xhr.send(fd);
});


});
