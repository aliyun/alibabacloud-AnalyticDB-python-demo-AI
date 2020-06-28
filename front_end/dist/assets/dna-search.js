'use strict';
var app = angular.module("dna_search_app", []);
// angular.module('myApp')
//     .filter('to_trusted', ['$sce', function($sce){
//         return function(text) {
//             return $sce.trustAsHtml(text);
//         };
//     }]);
app.controller("myCtrl", function($scope, $sce) {
    $scope.to_trusted = function(html_code) {
        return $sce.trustAsHtml(html_code);
    };
    $scope.dna_search = function() {
        if (document.getElementById('dna_sequence').value.length<50){
            document.getElementById("search_sequence").innerHTML = "序列长度不少于50, 当前长度"
                 +document.getElementById('dna_sequence').value.length;
            return;
        }

        // $scope.records = Array.apply(('病毒名', 'xxxxxxxxxxxx', "相似度值"), new Array(5));
        // $scope.records = Array.apply(['病毒名', 'xxxxxxxxxxxx', "相似度值"], new Array(10));
        // $scope.records = [
        //     ['133', 'GATCGACCGCATCGCCGCCAAGCTGGCCAGCACGGTGCCCCACTGGAAGGCGATGAACGACGATCAGCGGTGCGC' +
        //     'CGATCGACCGCATCGCCGCCAAGCTGGCCAGCACGGTGCCCCACTGGAAGGCGATGAACGACGATCAGCGGTGCGC', '病毒介绍',"0.99"],
        //     ['133', 'GATCGACCGCATCGCCGCCAAGCTGGCCAGCACGGTGCCCCACTGGAAGGCGATGAACGACGATCAGCGGTGCGC' +
        //     'CGATCGACCGCATCGCCGCCAAGCTGGCCAGCACGGTGCCCCACTGGAAGGCGATGAACGACGATCAGCGGTGCGC', '病毒介绍',"0.99"],
        //     ['133', 'GATCGACCGCATCGCCGCCAAGCTGGCCAGCACGGTGCCCCACTGGAAGGCGATGAACGACGATCAGCGGTGCGC' +
        //     'CGATCGACCGCATCGCCGCCAAGCTGGCCAGCACGGTGCCCCACTGGAAGGCGATGAACGACGATCAGCGGTGCGC', '病毒介绍',"0.99"],
        //     ['133', 'GATCGACCGCATCGCCGCCAAGCTGGCCAGCACGGTGCCCCACTGGAAGGCGATGAACGACGATCAGCGGTGCGC' +
        //     'CGATCGACCGCATCGCCGCCAAGCTGGCCAGCACGGTGCCCCACTGGAAGGCGATGAACGACGATCAGCGGTGCGC', '病毒介绍',"0.99"],
        //     ['133', 'GATCGACCGCATCGCCGCCAAGCTGGCCAGCACGGTGCCCCACTGGAAGGCGATGAACGACGATCAGCGGTGCGC' +
        //     'CGATCGACCGCATCGCCGCCAAGCTGGCCAGCACGGTGCCCCACTGGAAGGCGATGAACGACGATCAGCGGTGCGC', '病毒介绍',"0.99"],
        // ];
        // console.log($scope.records[0]);
        document.getElementById("search_result").classList.remove("d-none");
        var form = new FormData(document.getElementById("dna_search_form"));
        for(var pair of form.entries()) {
            console.log(pair[0]+ ', '+ pair[1]);
        }
        $.ajax({
            url: './dna_search/search',
            type: "post",
            data: form,
            processData: false,
            contentType: false,
            async: false,
            success: function (data) {
                console.log("success");
                console.log(data.result);
                let result = data.result;

                for (var i = 0; i < result.length; i++) {
                    result[i][1] = result[i][1].replace(new RegExp(result[i][4], "gi"), (match) => `<strong>${match}</strong>`);
                    result[i][1] = $sce.trustAsHtml(result[i][1]);
                    result[i][5] = $sce.trustAsHtml(result[i][5]);
                }
                // results.replace(new RegExp(term, "gi"), (match) => `<mark>${match}</mark>`);
                $scope.records = result;

                // let e = $("#show");
                // $("#show").html(data.result);
            },
            error: function (e) {
                console.log(e.responseText);
                alert("错误！！");
            }
        });
    }
});

document.getElementById('dna_sequence').onchange = function() {
    console.log(document.getElementById('dna_sequence').value);
    document.getElementById("search_sequence").innerHTML = "查询的基因序列:\n" +
        document.getElementById('dna_sequence').value;
}

function database_count() {
    $.ajax({
        url: './image_search/count',
        type: "get",
        processData: false,
        contentType: false,
        async: true,
        success: function (data) {
            console.log("success");
            console.log(data.result[0]);
            document.getElementById("count_value").innerHTML = "AnalyticDB中病毒基因总数:"+ 12182 + "</br>" +
                "AnalyticDB中基因片段总数:"+ 1590804;
        },
        error: function (e) {
            console.log(e.responseText);
            // alert("错误！！");
        }
    });
}


// var canvas = document.createElement("canvas");
// var canvas = document.getElementById("canvas_test");
// var context = canvas.getContext('2d');
//
// document.getElementById('image_url').onchange = function() {
//     // var img = document.getElementById("image_preview");
//     // img.crossOrigin = 'Anonymous';
//     // document.getElementById("image_preview").src = document.getElementById('image_url').value;
//     var xhr = new XMLHttpRequest();
//     xhr.onreadystatechange = function(){
//         if (this.readyState == 4 && this.status == 200){
//             //this.response is what you're looking for
//             // handler(this.response);
//             var reader = new FileReader();
//             reader.onload = function (e) {
//                 // get loaded data and render thumbnail.
//                 document.getElementById("image_preview").src = e.target.result;
//                 console.log(document.getElementById("image_preview").src);
//             };
//             // read the image file as a data URL.
//             reader.readAsDataURL(this.response);
//             // console.log(this.response, typeof this.response);
//             // var img = document.getElementById('img');
//             // var url = window.URL || window.webkitURL;
//             // img.src = url.createObjectURL(this.response);
//         }
//     };
//     if (document.getElementById('image_url').value.startsWith("data:"))
//         xhr.open('GET', document.getElementById('image_url').value);
//     else
//         xhr.open('GET', "https://cors-anywhere.herokuapp.com/" + document.getElementById('image_url').value);
//     xhr.responseType = 'blob';
//     xhr.send();
//
// };
//
// function getBase64Image(img) {
//     var canvas = document.createElement("canvas");
//     var context = canvas.getContext('2d');
//     canvas.width = img.width;
//     canvas.height = img.height;
//     context.drawImage(img, 0, 0);
//     var dataURL = canvas.toDataURL("image/jpeg");
//     return dataURL;
// }
//
//
//
// function dataURItoBlob(dataURI) {
//     // convert base64/URLEncoded data component to raw binary data held in a string
//     var byteString;
//     if (dataURI.split(',')[0].indexOf('base64') >= 0)
//         byteString = atob(dataURI.split(',')[1]);
//     else
//         byteString = unescape(dataURI.split(',')[1]);
//     // separate out the mime component
//     var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
//     // write the bytes of the string to a typed array
//     var ia = new Uint8Array(byteString.length);
//     for (var i = 0; i < byteString.length; i++) {
//         ia[i] = byteString.charCodeAt(i);
//     }
//     return new Blob([ia], {type: mimeString});
// }

// $("input[type=file]").change(function () {
//     var fieldVal = $(this).val();
//     if (fieldVal != undefined || fieldVal != "") {
//         $(this).next(".custom-file-label").text(fieldVal);
//     }
// });



