import unittest
from final_project import *

class TestDatabase(unittest.TestCase):

    def test_comminity_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT Name FROM Communities'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Amalfi',), result_list)
        self.assertEqual(len(result_list), 97)

        sql = '''
            SELECT State, count(*)
            FROM Communities
            Group By State
            ORDER BY count(*) DESC
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        #print(result_list)
        self.assertEqual(len(result_list), 5)
        self.assertEqual(result_list[0][1], 66)

        conn.close()

    def test_details_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT Community
            FROM Details
            WHERE Area=1000
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Traver Ridge',), result_list)
        self.assertEqual(len(result_list), 11)

        sql = '''
            SELECT count(*)
            FROM Details
            WHERE Community = 'Amalfi'
        '''
        results = cur.execute(sql)
        count = results.fetchone()[0]
        self.assertEqual(count, 6)

        conn.close()

    def test_joins(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT Communities.City
            FROM Communities
                JOIN Details
                ON Communities.Id = Details.CommunityId
            WHERE Details.Area=500
                AND Details.Bedroom="Studio"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Ann Arbor',), result_list)
        conn.close()

class TestCommunityScrape(unittest.TestCase):
    Communities = {}
    Rent={}
    feature={}
    get_communities_for_state('Michigan')
    def test_community_list(self):
        self.assertIn("Traver Ridge", Communities)
        self.assertEqual(len(Communities),26)
        self.assertEqual("1 Bedroom", Rent['Meadowbrook Village']['type1']['bed'])
        self.assertIn("Play Yard", feature['Silver Lake Hills'])
        self.assertIn("Double Tennis Court",feature['Traver Ridge'])


class Test_info_section(unittest.TestCase):
    def test_select_state(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        state = select_state('MI')
        MI_list = state.fetchall()
        self.assertIn(('Meadowbrook Village',), MI_list)

    def test_contact(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        contact = contact_information('Silver Lake Hills')
        contact_list = contact.fetchall()
        self.assertEqual('810-714-5555',contact_list[0][0])

    def test_address(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        address =  address_info('Silver Lake Hills')
        address_list = address.fetchall()
        self.assertEqual('3200 Foley Glen Drive',address_list[0][0])

    def test_feature(self):
        feature = feature_info('Silver Lake Hills')
        self.assertIn('24-Hour Computer Lab & Fitness Center',feature)

    def test_details(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        details = details_info('Silver Lake Hills')
        detail_list = details.fetchall()
        self.assertEqual('$809 - $829',detail_list[0][2])

class TestPlot(unittest.TestCase):
    def test_plot(self):
        try:
            y1,x1,y2,x2=plot_compartion("Traver Ridge","Evergreen")
            plot_bar_chart(y1,x1,y2,x2,"Traver Ridge","Evergreen")
        except:
            self.fail()

unittest.main()
