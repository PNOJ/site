

let ace_language_map = {
    "": "plain_text",
    "python3": "python",
    "java8": "java",
    "cpp17": "c_cpp",
    "haskell": "haskell",
    "brainfuck": "plain_text",
    "c18": "c_cpp",
    "java11": "java",
    "scratch": "json",
    "text": "plain_text",
};

var app = new Vue({
    el: '.submit-card',
    data: {
        language: '',
        // submit_button_text: 'Submit',
    },
    methods: {
        source: function (newSource, oldSource) {
            if (newSource.srcElement.files[0].name.endsWith(".sb3")) {
                JSZip.loadAsync(newSource.srcElement.files[0]).then(function(zip) {
                    let sb3project = zip.file("project.json");
                    if (sb3project == null) {
                        editor.setValue("Whoops! If you uploaded a Scratch project, please ensure it is a valid .sb3 project. Otherwise, please upload a text file, not a zip file.");
                    } else {
                        sb3project.async("string").then(result => {
                            editor.setValue(result);
                        });
                    }
                });
            } else if (newSource.srcElement.files[0].name.endsWith(".sb2") || newSource.srcElement.files[0].name.endsWith(".sb")) {
                editor.setValue("Whoops! Only .sb3 projects are supported.");
            } else if (!newSource.srcElement.files[0].type.startsWith("text")) {
                editor.setValue("Whoops! The file you uploaded doesn't look like a text file. If it is a text file, please paste the code into this code editor.");
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

    // app.submit_button_text = "Please wait...";

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
