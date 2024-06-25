class Pnations {

        constructor(val, callback) {
            this.page = 1;
            this.count = 0;
            this.val = val;
            this.callback = callback;
        }

        nation_pre () {
            // console.log("nation_pre", this.page);
            if (this.page > 1) {
                this.page = (this.page * 1) - 1;
                this.callback();
            }
        }

        nation_next () {
            // console.log("nation_next", this.page, this.count);
            if (this.page < this.count) {
                this.page = (this.page * 1) + 1;
                this.callback();
            }
        }

        nation_page (val) {
            // console.log("nation_page", this.page);
            this.page = val;
            this.callback();
        }

        nation_display (done) {
            let cname = this.val['cname']
            // console.log("nation_display");
            let table_id = this.val['table_id'];
            // let results = val['results'];
            let results = done;

            let range = this.val['range'];
            // console.table('results', results);
            let has_previous = results.previous;
            let has_next = results.next;
            this.count = results.count;

            let range_first = 1;
            let range_last = Math.ceil(this.count / this.val['page_size']);
            // console.log('range_last', range_last);

            for (let x = 0; (range * x) < this.page; x++) {
                range_first = (range * x) + 1;
            }

            // console.log('page', this.page);
            // console.log('range', range);
            // console.log('range_first', range_first);


            let nation = "";
            nation += "<ul class='pagination'>";

            if (has_previous) {
                nation += "<li class='page-item'> <a class='page-link' onclick='" + cname + ".nation_page(1);'> &laquo;처음 </a> </li>";
                nation += "<li class='page-item'> <a class='page-link' onclick='" + cname + ".nation_pre();'>이전</a> </li>";
            } else {
                nation += "<li class='page-item disabled'> <a class='page-link'> &laquo;처음 </a> </li>";
                nation += "<li class='page-item disabled'> <a class='page-link'>이전</a> </li>";
            }
            for (let p = range_first; (p < range + range_first) && (p <= range_last); p++) {
                if (this.page == p) {
                    nation += "<li class='page-item active'> <a class='page-link'>" + p + "</a> </li>";
                } else {
                    nation += "<li class='page-item'> <a class='page-link' onclick='" + cname + ".nation_page(" + p + ");'>" + p + "</a> </li>";
                }
            }
            if (has_next) {
                nation += "<li class='page-item'> <a class='page-link' onclick='" + cname + ".nation_next();'>다음</a> </li>";
                // nation += "<li class='page-item'> <a class='page-link' onclick='nation_next();'>다음</a> </li>";
                nation += "<li class='page-item'> <a class='page-link' onclick='" + cname + ".nation_page(" + range_last + ");'>마지막 &raquo;</a> </li>";
            } else {
                nation += "<li class='page-item disabled'> <a class='page-link'>다음</a> </li>";
                nation += "<li class='page-item disabled'> <a class='page-link'>마지막</a> </li>";
            }
            nation += "</ul>";

            $('#' + table_id).html(nation);
        }
    }