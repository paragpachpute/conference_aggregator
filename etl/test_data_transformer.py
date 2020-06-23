from unittest import TestCase

from database.proceeding_home import ProceedingHome
from entity.proceeding import Proceeding
from etl.data_transformer import DataTransformer


class TestDataTransformer(TestCase):
    def setUp(self) -> None:
        database = "test_database2"
        self.transformer = DataTransformer()
        self.proceeding_home = ProceedingHome(database)

    def test_transform_proceeding(self):
        criteria = {"proceeding_key": "conf/3dor/2017"}
        p = self.proceeding_home.get_proceedings(criteria)
        proceeding = Proceeding(**p[0])
        occurrence_instance, series_instance = self.transformer.transform_proceeding(proceeding)

        self.assertEqual(2, len(occurrence_instance['parent']))
        self.assertEqual('workshop_occurrence', occurrence_instance['invitation_type'])
        self.assertEqual('workshop_series', series_instance['invitation_type'])
        self.assertEqual(
            "10th Eurographics Workshop on 3D Object Retrieval, 3DOR@Eurographics 2017, Lyon, France, April 23-24, 2017",
            occurrence_instance['title'])

        print(occurrence_instance)
        print(series_instance)
