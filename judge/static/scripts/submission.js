var app = new Vue({
    el: '.result-card',
    data: {
        submission: {},
    },
    methods: {
        get_status_color: function(status_code) {
            return 'text-' + status_colors[status_code.toLowerCase()]
        },
        poll: function() {
            if (this.submission.status == undefined || this.submission.status == 'G') {
                let fetch_promise = fetch(window.location.pathname + '/data');
                fetch_promise.then(response => {
                    if (response.ok) {
                        let json_promise = response.json();
                        json_promise.then(data => {
                            this.submission = data;
                        });
                    } else {
                        alert("Error while fetching submission data: " + response.status);
                    }
                });
            }
        }
    },
    computed: {
    },
    watch: {
    },
    mounted() {
        this.poll();

        setInterval(this.poll, 1000); 
    }
})

let submission_data;

function round(num) {
    return Math.round(num*10)/10;
};

let status_colors = {
    'ac': 'success',
    'wa': 'danger',
    'tle': 'info',
    'mle': 'info',
    'ole': 'info',
    'ir': 'warning',
    'ce': 'secondary',
    'g': 'light',
    'ie': 'secondary',
    'md': 'light',
    'ab': 'secondary',
};
