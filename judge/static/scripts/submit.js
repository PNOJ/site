

let ace_language_map = {
    "": "plain_text",
    "py3": "python",
    "java8": "java",
    "c++17": "c_cpp",
};

var app = new Vue({
    el: '.submit-card',
    data: {
        language: '',
    },
    methods: {
        source: function (newSource, oldSource) {
            if (!newSource.srcElement.files[0].type.startsWith("text")) {
                editor.setValue("¯\\_(ツ)_/¯");
            } else {
                var reader = new FileReader();
                reader.onload = function(e) {
                    editor.setValue(e.target.result);
                };
                reader.readAsText(newSource.srcElement.files[0]);
            }
        },
    },
    watch: {
        language: function (newLanguage, oldLanguage) {
            editor.session.setMode("ace/mode/" + ace_language_map[newLanguage]);
        },
    }
})

// function submitSolution() {
//     // var fileinput = document.getElementById("id_source");
//     // var filelist = new FileList(file);
//     var formData = new FormData());
// }

var submission_form = document.getElementById("problem_submit_form");

submission_form.onsubmit = async (e) => {
    e.preventDefault();

    var file = new File([editor.getValue()], "submission.txt", {type: "text/plain"});
    var formData = new FormData(submission_form);
    formData.set("source", file, "submission.txt");
    let response = await fetch(window.location.pathname, {
        method: 'POST',
        body: formData,
    });
    var res = await response;
    window.location.replace(res.url);
};

var editor = ace.edit("editor");
