#!/usr/bin/env python

"""
    django-reversion-compare unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    I used the setup from reversion_compare_test_project !

    TODO:
        * models.OneToOneField()
        * models.IntegerField()

    :copyleft: 2012-2022 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from bx_django_utils.test_utils.html_assertion import assert_html_response_snapshot, get_django_name_suffix
from freezegun import freeze_time
from override_storage import locmem_stats_override_storage
from override_storage.utils import Stats
from reversion import create_revision, is_registered
from reversion.models import Revision, Version

from reversion_compare_project.models import VariantModel
from reversion_compare_project.utils.fixtures import Fixtures
from reversion_compare_project.utils.test_cases import BaseTestCase


class VariantModelNoDataTest(BaseTestCase):
    """
    Tests with a empty VariantModel
    """

    def test_textfield(self):
        with create_revision():
            item = VariantModel.objects.create(
                text="""\
first line
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut
labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit
esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.
last line"""
            )
            item.save()

        with create_revision():
            item.text = """\
first line
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut
labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat. Duis added aute irure dolor in reprehenderit in voluptate velit
esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.
last line"""
            item.save()

        response = self.client.get(
            "/en/admin/reversion_compare_project/variantmodel/1/history/compare/",
            data={"version_id2": 1, "version_id1": 2},
        )
        self.assertEqual(response.status_code, 200, response)
        self.assertContains(response, "<ins>added </ins>", msg_prefix=response.content.decode())


@locmem_stats_override_storage(name='storage_stats')
class VariantModelWithDataTest(BaseTestCase):
    """
    Tests with VariantModel and existing data from Fixtures()
    """

    storage_stats: Stats = None

    def setUp(self):
        super().setUp()

        self.item, self.fixtures = Fixtures(verbose=False).create_VariantModel_data()

        self.assertEqual(
            dict(self.storage_stats.saves_by_field),
            {('reversion_compare_project', 'variantmodel', 'file_field'): 'file_field_19.txt'},
        )
        self.assertEqual(self.storage_stats.save_cnt, 21)

        queryset = Version.objects.get_for_object(self.item)
        self.version_ids = queryset.values_list("pk", flat=True)

    def test_initial_state(self):
        self.assertTrue(is_registered(VariantModel))

        self.assertEqual(VariantModel.objects.count(), 1)

        count = len(self.fixtures) + 1  # incl. initial

        self.assertEqual(Version.objects.get_for_object(self.item).count(), count)
        self.assertEqual(Revision.objects.all().count(), count)
        self.assertEqual(len(self.version_ids), count)

    @freeze_time('2024-02-01')
    def test_all_changes(self):
        self.client.force_login(self.user)

        # debug_response(self.client.get("/admin/reversion_compare_project/variantmodel/1/history/"))
        # compare initial with last version
        response = self.client.get(
            "/en/admin/reversion_compare_project/variantmodel/1/history/compare/",
            data={"version_id2": 1, "version_id1": len(self.fixtures) + 1},  # incl. initial
        )
        self.assertEqual(response.status_code, 200, response)

        field_headlines = [f"<h3>{field_name.replace('_', ' ')}</h3>" for field_name, value in self.fixtures]
        self.assert_html_parts(response, parts=field_headlines)
        self.assert_html_parts(
            response,
            parts=(
                "<h3>boolean</h3>",
                '<p class="highlight"><del>False</del> changed to: <ins>True</ins></p>',
                "<h3>null boolean</h3>",
                '<p class="highlight"><del>None</del> changed to: <ins>False</ins></p>',
                "<h3>char</h3>",
                "<del>- a</del>",
                "<ins>+ B</ins>",
                "<h3>choices char</h3>",
                "<del>- alpha</del>",
                "<ins>+ bravo</ins>",
                "<h3>text</h3>",
                "<del>- Foo &#39;one&#39;</del>",
                "<ins>+ Bar &#39;two&#39;</ins>",
                "<h3>integer</h3>",
                "<del>- 0</del>",
                "<ins>+ -1</ins>",
                "<h3>integers</h3>",
                "<del>- 1,2,3</del>",
                "<ins>+ 2,3,4</ins>",
                "<h3>positive integer</h3>",
                "<del>- 1</del>",
                "<ins>+ 3</ins>",
                "<h3>big integer</h3>",
                "<del>- -9223372036854775808</del>",
                "<ins>+ 9223372036854775807</ins>",
                "<h3>time</h3>",
                "<del>- 20:15:00</del>",
                "<ins>+ 19:30:00</ins>",
                "<h3>date</h3>",
                "<del>- 1941-05-12</del>",
                "<ins>+ 2099-12-31</ins>",
                "<h3>datetime</h3>",
                "<del>- Aug. 19, 2005, 8:13 a.m.</del>",
                "<ins>+ Jan. 1, 2000, midnight</ins>",
                "<h3>decimal</h3>",
                "<del>- 1.23456789</del>",
                "<ins>+ 3.1415926535</ins>",
                "<h3>float</h3>",
                "<del>- 2.345</del>",
                "<ins>+ 3.1415</ins>",
                "<h3>email</h3>",
                "<del>- one@foo-bar.com</del>",
                "<ins>+ two@foo-bar.com</ins>",
                "<h3>url</h3>",
                """
                <div class="module">
                    <pre class="highlight">
                    <span class="diff-line diff-del diff-ins">http<ins>s</ins>://
                    <del>www.pylucid.org</del><ins>github.com/jedie</ins>/</span>
                    </pre>
                </div>
                """,
                "<h3>file field</h3>",
                """
                <div class="module">
                    <pre class="highlight">
                    <span class="diff-line diff-ins">/media/file_field<ins>_19</ins>.txt</span>
                    </pre>
                </div>
                """,
                "<h3>filepath</h3>",
                """
                <div class="module">
                    <pre class="highlight"><del>- foo/</del>
                    <ins>+ bar/</ins></pre>
                </div>
                """,
                "<h3>ip address</h3>",
                "<del>- 192.168.0.1</del>",
                "<ins>+ 10.0.0.0</ins>",
                #
                '<h3>json field</h3>',
                '<del>456</del><ins>&#x27;XXX&#x27;</ins>',
            ),
        )
        assert_html_response_snapshot(
            response,
            validate=False,
            query_selector='#content',
            name_suffix=get_django_name_suffix(),
        )
