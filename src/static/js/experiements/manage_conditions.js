var groupBy = function(array, grouperFn) {
    // Example of using groupBy
    // array = [
    //      {label: 'A', val: 1},
    //      {label: 'B', val: 2},
    //      {label: 'A', val: 3}
    // ]
    // groupBy(array, function (obj) {return obj.label;})
    // [{
    //     grouped: [
    //          {label: 'A', val: 1},
    //          {label: 'A', val: 3},
    //     ],
    //     key: 'A'
    // }, {
    //     grouped: [
    //          {label: 'B', val: 2},
    //     ],
    //     key: 'B'
    // }]
    var groups = {};
    array.forEach(function(o)
    {
        var key = grouperFn(o);
        var keyStr = JSON.stringify(key);
        groups[keyStr] = groups[keyStr] || {key: key, grouped: []};
        groups[keyStr].grouped.push(o);
    });
    return Object.keys(groups).map(function(group) {
        return groups[group];
    });
};


var vm = new Vue({
    el: '#app',
    // data are from the template HTML
    data: vueAppData,
    computed: {
        userDefinedConditions: function() {
            return this.conditions.filter(
                function(cond){ return cond._uid > 0; }
            );
        },
        filteredDataSources: function() {
            var filterStr = this.sourceFilter;
            return this.dataSources.filter(function(source) {
                return source.file_path.indexOf(filterStr.filePath) > -1 &&
                    source.file_type.indexOf(filterStr.fileType) > -1 &&
                    source.sample.indexOf(filterStr.sample) > -1;
            });
        },
        selectedDataSources: function() {
            return this.dataSources.filter(function (source) {
                return source.selected;
            });
        },
        canRenameSample: function() {
            var anyFilter = Object.values(this.sourceFilter).reduce(
                    function (prev, cur) { return prev || cur; }
                ) === "";
            return !anyFilter;
        },
        fastqDataSources: function() {
            return this.dataSources.filter(
                function (source) {
                    return source.file_type === 'FASTQ';
                }
            );
        },
        fastqSourcesBySample: function() {
            var groupedSources = groupBy(
                this.fastqDataSources,
                function (source) { return source.sample; }
            ).filter(function (group) {
                return !!group.key;
            });
            return groupedSources.map(function(group) {
                // if all sources' condition are the same, keep it
                var allSelected = group.grouped.every(function(source, index, array){
                    return source.selected === true;
                });
                return {
                    sample: group.key,
                    files: group.grouped.map(function(source) {
                        return {
                            pk: source.data_source_pk,
                            label: (
                                source.file_path + ' (' +
                                source.file_type +
                                (source.metadata.strand ? (', ' + source.metadata.strand) : '') +
                                ')'
                            )
                        };
                    }),
                    selected: allSelected
                };
            });

        },
        dataSourcesBySample: function() {
            var groupedSources = groupBy(
                this.selectedDataSources,
                function (source) { return source.sample; }
            );
            return groupedSources.map(function(group) {
                // if all sources' condition are the same, keep it
                var equalCondition = group.grouped.map(
                    function (source) { return source.condition; }
                ).every(function(value, index, array){
                    return value === array[0];
                });
                return {
                    sample: group.key,
                    files: group.grouped.map(function(source) {
                        return {
                            pk: source.data_source_pk,
                            label: (
                                source.file_path + ' (' +
                                source.file_type +
                                (source.metadata.strand ? (', ' + source.metadata.strand) : '') +
                                ')'
                            )
                        };
                    }),
                    condition: equalCondition ? group.grouped[0].condition : 0
                };
            });
        },
        dataSourcesByCondition: function() {
            var conditions = this.conditions;
            return groupBy(
                this.dataSourcesBySample,
                function (grp) { return grp.condition; }
            ).map(function (condGroup) {
                return {
                    condition: conditions[condGroup.key],
                    samples: condGroup.grouped.map(function(g) { return g.sample; })
                };
            });
        }
    },
    methods: {
        removeCondition: function(index, event) {
            // remove current condition
            this.conditions.splice(index, 1);
        },
        addCondition: function(label) {
            var defaultLabel = 'New condition ' + this.numConditionCreated;
            this.conditions.push({
                '_uid': this.numConditionCreated,
                'label': label ? label.trim() : defaultLabel
            });
            this.numConditionCreated += 1;
        },
        leaveEditMode: function() {
            // trim leading and trailing spaces of all conditions
            this.conditions.forEach(function (condition) {
                condition.label = condition.label.trim();
            });
            this.editable = false;
        },
        enterEditMode: function() {
            this.editable = true;
        },
        updateFilteredSourcesSelectedStatus: function(status) {
            // Alter the filtered data sources select status
            // based on the selectedStatus
            this.filteredDataSources.forEach(function(source) {
                source.selected = status;
            });
        },
        clearAllFilters: function() {
            var filters = this.sourceFilter;
            Object.keys(this.sourceFilter).forEach(function(f) {
                Vue.set(filters, f, '');
            });
        },
        renameFilteredSourcesName: function() {
            var newName = this.newSampleName;
            this.filteredDataSources.forEach(function(source) {
                source.sample = newName;
            });
        },
        updateSourceCondition: function(sample, conditionId) {
            // Binding to condition ID makes things easier
            this.selectedDataSources.filter(function(source) {
                return source.sample === sample;
            }).forEach(function(source) {
                source.condition = conditionId;
            });
        },
        toggleSourceBySample: function(sample, event) {
            console.log(sample, event.target.checked);
            var newSelectedStatus = event.target.checked;
            this.fastqDataSources.filter(function(source) {
                return source.sample === sample;
            }).forEach(function(source) {
                source.selected = newSelectedStatus;
            });
        }
    }
});

// Add two default conditions if no condition is already given
if (vm.conditions.length == 0) {
    vm.addCondition('(All)');
    vm.addCondition('Control');
    vm.addCondition('Test');
}


// When posting the form, put the condition and data source selection and
// annotation info as the value of a newly created hidden input
$form = $('#new-experiment-form');
$form.submit(function() {
    var $input = $('<input type="hidden" name="extraData">');
    $input.val(JSON.stringify({
        conditions: vm.conditions,
        numConditionCreated: vm.numConditionCreated,
        dataSources: vm.dataSources
    }));
    $(this).append($input);
    return true;
});

$("#submit-form").click(function() {
    $form.submit();
});
