var vm = new Vue({
    el: '#app',
    data: {
        editable: true,
        conditions: [
        ],
        numConditionCreated: 0,
        sourceFilter: '',
        dataSources: data_sources
    },
    computed: {
        filteredDataSources: function() {
            var filterStr = this.sourceFilter;
            return this.dataSources.filter(function (source) {
                return source.file_path.indexOf(filterStr) > -1;
            });
        },
        selectedDataSources: function() {
            var filterStr = this.sourceFilter;
            return this.dataSources.filter(function (source) {
                return source.selected;
            });
        }
    },
    methods: {
        removeCondition: function (index, event){
            // remove current condition
            this.conditions.splice(index, 1);
        },
        addCondition: function (label) {
            var defaultLabel = 'New condition ' + (this.numConditionCreated + 1);
            this.conditions.push({
                '_uid': this.numConditionCreated,
                'label': label ? label.trim() : defaultLabel
            });
            this.numConditionCreated += 1;
        },
        leaveEditMode: function (){
            // trim leading and trailing spaces of all conditions
            this.conditions.forEach(function (curVal) {
                curVal.label = curVal.label.trim();
            });
            this.editable = false;
        },
        enterEditMode: function() {
            this.editable = true;
        },
        alterFilteredSourcesSelectedStatus: function(status) {
            // Alter the filtered data sources select status
            // based on the selectedStatus
            this.filteredDataSources.forEach(function (source) {
                source.selected = status;
            });
        }
    }
});

// Add two default conditions
vm.addCondition('Control');
vm.addCondition('Test');
