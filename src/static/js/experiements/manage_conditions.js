new Vue({
    el: '#conditions',
    data: {
        newCondition: '',
        conditions: [
            // { text: 'Add new conditions' }
        ]
    },
    methods: {
        addCondition: function () {
            var text = this.newCondition.trim();
            if (text) {
                this.conditions.push({ text: text });
                this.newCondition = '';
            }
        },
        removeCondition: function (index) {
            this.conditions.splice(index, 1);
        }
    }
})
