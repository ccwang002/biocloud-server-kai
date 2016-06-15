from crispy_forms.layout import Field, Fieldset, HTML, Layout, Submit
from django.utils.timezone import now


class AnalysisCommonLayout(Layout):

    def __init__(self, *fields, analysis_type="Abstract Analysis"):
        """Form layout building block for all Analysis form classes

        It define the two main shared form blocks, rendered in HTML
        as fieldsets``<fieldset>...</fieldset>`` including:

        1. Analysis name and description (via :attr:`description_fieldset`)
        2. Experiment selection (containing sample and condition)
           (via :attr:`sample_condition_fieldset`)

        One can feel free to subclass this and alter the way how these two
        fields are rendered (if needed).

        For experiment selection fieldset, it contain the necessary HTML
        component that embed the Vue.js application and component to display
        the experiment info. This particular component can be modified via
        :attr:`experiment_info_vue_html`.

        Args:
            analysis_type (str): Type of the analysis,e.g., RNA-Seq.

        Attributes:
            name_description_fieldset (Fieldset):
                Analysis name and description form block.

            sample_condition_fieldset (Fieldset):
                Experiment selection form block.

            experiment_info_vue_html (HTML):
                Experiment info display Vue.js app entry and component.

        To use this layout for your own analysis form::

            class MyAdvSeqAnalysisForm(AbstractAnalysisCreateForm):

                @cached_property
                def helper(self):
                    helper = FormHelper()
                    helper.include_media = False
                    helper.layout = Layout(
                        AnalysisCommonLayout(analysis_type="MyAdvSeq"),
                        # Put rest of your fields and layouts
                        # in the following as usual, for example,
                        Fieldset(
                            Field('adv_seq_param'),
                            ...
                        ),
                        FormActions(Submit(...)),
                    )
                    return helper

        """
        self.name_description_fieldset = Fieldset(
            'Analysis description',
            Field(
                'name', value=(
                    '{analysis_type:s} {now:%Y-%m-%d %H:%M}'
                        .format(analysis_type=analysis_type, now=now())
                )
            ),
            Field('description'),
        )
        self.experiment_info_vue_html = HTML(
            "{% include 'analyses/_includes/experiment_info_vue.html' %}"
        )
        self.sample_condition_fieldset = Fieldset(
            'Samples and Conditions',
            HTML("<p>Specify your experiment here.</p>"),
            Field('experiment'),
            self.experiment_info_vue_html
        )

        super().__init__(
            Layout(
                self.name_description_fieldset,
                self.sample_condition_fieldset,
            ),
            *fields,
        )


