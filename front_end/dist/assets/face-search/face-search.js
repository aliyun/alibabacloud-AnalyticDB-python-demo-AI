'use strict';
var app = angular.module("image_search_app", []);
app.controller("myCtrl", function($scope) {
    $scope.image_search = function() {
        var form = new FormData(document.getElementById("image_search_form"));
        form.append("image", document.getElementById("image_preview").src);
        // form.append("image", getBase64Image(document.getElementById("image_preview")));
        for(var pair of form.entries()) {
            console.log(pair[0]+ ', '+ pair[1]);
        }
        $.ajax({
            url: './face_search/search',
            type: "post",
            data: form,
            processData: false,
            contentType: false,
            async: false,
            success: function (data) {
                console.log("success");
                console.log(data.result);
                $scope.records = data.result

                // let e = $("#show");
                // $("#show").html(data.result);
            },
            error: function (e) {
                console.log(e.responseText);
                alert("错误！！, 未检测到人脸");
            }
        });
    }
});

function insert_image() {
    // read the image file as a data URL.
    var files = document.getElementById("file_insert").files;
    var num_success = 0;
    var num_fail = 0;
    var num_total = files.length;
    for (var i = 0; i < files.length; i++) {
        document.getElementById("insert_msg").innerHTML = "";
        var reader = new FileReader();
        // console.log(files[i].name);
        reader.onload = function (e) {
            var form = new FormData(document.getElementById("image_search_form"));
            // get loaded data and render thumbnail.
            console.log(e.target.filename);
            form.append("image", e.target.result);
            form.append("image_name", e.target.filename);
            // for(var pair of form.entries()) {
            //     console.log(pair[0]+ ', '+ pair[1]);
            // }
            $.ajax({
                url: './face_search/insert',
                type: "post",
                data: form,
                processData: false,
                contentType: false,
                // context:"insert_msg",
                async: true,
                success: function (data) {
                    num_success = num_success + 1;
                    console.log("导入成功: " + num_success + "/" + num_total +  ", 失败: " +  num_fail);
                    // document.getElementById("insert_msg").innerHTML = "导入成功: " + num_success + "/" + num_total +  ", 失败: " +  num_fail;
                    },
                error: function (e) {
                    num_fail = num_fail + 1;
                    console.log(e.responseText);
                    // alert("错误！！");
                }
            });
        };
        reader.filename = files[i].name;
        reader.readAsDataURL(files[i]);


    }
    var id = setInterval(function(){
        if (num_success + num_fail >= num_total)
            {
                clearInterval(id);
            }
        document.getElementById("insert_msg").innerHTML = "导入成功: " + num_success + "/" + num_total +  ", 失败: " +  num_fail;
    }, 1000);

}


document.getElementById("file_insert").onchange = function () {
    document.getElementById("insert_msg").innerHTML = "";
    var num = document.getElementById("file_insert").files.length;
    document.getElementById("insert_msg").innerHTML = "已选择" +  num +  "个文件";
};

function database_count() {
    $.ajax({
        url: './face_search/count',
        type: "get",
        processData: false,
        contentType: false,
        async: true,
        success: function (data) {
            console.log("success");
            console.log(data.result[0]);
            document.getElementById("count_value").innerHTML = "AnalyticDB中图片总数:"+ data.result[0];
        },
        error: function (e) {
            console.log(e.responseText);
            // alert("错误！！");
        }
    });
}

// 预览图片文件
document.getElementById("image_file").onchange = function () {
    var reader = new FileReader();
    reader.onload = function (e) {
        // get loaded data and render thumbnail.
        document.getElementById("image_preview").src = e.target.result;
    };
    // read the image file as a data URL.
    reader.readAsDataURL(this.files[0]);
};

document.getElementById('image_url').onchange = function() {
    // var img = document.getElementById("image_preview");
    // img.crossOrigin = 'Anonymous';
    // document.getElementById("image_preview").src = document.getElementById('image_url').value;
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function(){
        if (this.readyState == 4 && this.status == 200){
            //this.response is what you're looking for
            // handler(this.response);
            var reader = new FileReader();
            reader.onload = function (e) {
                // get loaded data and render thumbnail.
                document.getElementById("image_preview").src = e.target.result;
                console.log(document.getElementById("image_preview").src);
            };
            // read the image file as a data URL.
            reader.readAsDataURL(this.response);

        }
    };
    if (document.getElementById('image_url').value.startsWith("data:"))
        xhr.open('GET', document.getElementById('image_url').value);
    else
        xhr.open('GET', "https://cors-anywhere.herokuapp.com/" + document.getElementById('image_url').value);
    xhr.responseType = 'blob';
    xhr.send();

};

function getBase64Image(img) {
    var canvas = document.createElement("canvas");
    var context = canvas.getContext('2d');
    canvas.width = img.width;
    canvas.height = img.height;
    context.drawImage(img, 0, 0);
    var dataURL = canvas.toDataURL("image/jpeg");
    return dataURL;
}



function dataURItoBlob(dataURI) {
    // convert base64/URLEncoded data component to raw binary data held in a string
    var byteString;
    if (dataURI.split(',')[0].indexOf('base64') >= 0)
        byteString = atob(dataURI.split(',')[1]);
    else
        byteString = unescape(dataURI.split(',')[1]);
    // separate out the mime component
    var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
    // write the bytes of the string to a typed array
    var ia = new Uint8Array(byteString.length);
    for (var i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ia], {type: mimeString});
}




