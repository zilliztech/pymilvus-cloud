import pytest

from milvus_cloud import ParamError
from factorys import records_factory

dim = 128
nq = 100


class TestGetVectorByID:
    def test_get_entity_by_id(self, gcon, gcollection):
        vectors = records_factory(128, 1000)
        ids = [i for i in range(1000)]
        status, ids_out = gcon.insert(collection_name=gcollection, records=vectors, ids=ids)
        assert status.OK(), status.message

        gcon.flush([gcollection])

        status, vec = gcon.get_entity_by_id(gcollection, ids_out[0:10])
        assert status.OK()
        assert len(vec) == 10

        for v in vec:
            assert len(v) == 128

    @pytest.mark.parametrize("v_id", [None, "", [], {"a": 1}, (1, 2)])
    def test_get_entity_by_id_invalid_id(self, v_id, gcon):
        with pytest.raises(ParamError):
            gcon.get_entity_by_id("test_get_entity_by_id_invalid_id", [v_id])

    @pytest.mark.parametrize("collection", [None, -1, [], {"a": 1}, (1, 2)])
    def test_get_entity_by_id_invalid_collecton(self, collection, gcon):
        with pytest.raises(ParamError):
            gcon.get_entity_by_id(collection, [1])

    def test_get_entity_by_id_non_existent_collection(self, gcon):
        status, _ = gcon.get_entity_by_id("non_existent", [1])
        assert not status.OK()

    def test_get_entity_by_id_with_empty_collection(self, gcon, gcollection):
        status, _ = gcon.get_entity_by_id(gcollection, [1])
        assert not status.OK()

    @pytest.mark.parametrize("ids", [[0], [9999]])
    def test_get_entity_by_id_non_existent_id(self, ids, gcon, gvector):
        status, vector = gcon.get_entity_by_id(gvector, ids)
        assert status.OK()
        # assert not vector


class TestDeleteByID:
    def test_delete_entity_by_id_normal(self, gcon, gcollection):
        vectors = records_factory(dim, nq)
        status, ids = gcon.insert(gcollection, vectors)
        gcon.flush([gcollection])
        assert status.OK()

        status = gcon.delete_entity_by_id(gcollection, ids[0:10])
        assert status.OK()

    @pytest.mark.parametrize("id_", [None, "123", []])
    def test_delete_entity_by_id_invalid_id(self, id_, gcon, gcollection):
        with pytest.raises(ParamError):
            gcon.delete_entity_by_id(gcollection, id_)

    @pytest.mark.skip
    def test_delete_entity_by_id_succeed_id(self, gcon, gcollection):
        vectors = records_factory(dim, nq)
        status, ids = gcon.insert(gcollection, vectors)
        assert status.OK()

        gcon.flush([gcollection])

        ids_exceed = [ids[-1] + 10]
        status = gcon.delete_entity_by_id(gcollection, ids_exceed)
        assert not status.OK()


class TestGetVectorID:
    def test_get_vector_id(self, gcon, gvector):
        status, info = gcon.get_collection_stats(gvector)
        assert status.OK()

        seg0 = info["partitions"][0]["segments"][0]
        status, ids = gcon.list_id_in_segment(gvector, seg0["name"])
        assert status.OK()
        assert isinstance(ids, list)
        assert len(ids) == 10000

    @pytest.mark.parametrize("collection", [None, "", [], {"a": 1}, (1, 2), True, False])
    def test_get_vector_id_invalid_collection(self, collection, gcon):
        with pytest.raises(ParamError):
            gcon.list_id_in_segment(collection, "test")

    @pytest.mark.parametrize("segment", [None, "", [], {"a": 1}, (1, 2), True, False])
    def test_get_vector_id_invalid_segment(self, segment, gcon):
        with pytest.raises(ParamError):
            gcon.list_id_in_segment("test", segment)

    def test_get_vector_id_non_existent(self, gcon, gvector):
        status, _ = gcon.list_id_in_segment(gvector, "segment")
        assert not status.OK()

        status, info = gcon.get_collection_stats(gvector)
        assert status.OK()
        seg0 = info["partitions"][0]["segments"][0]
        status, _ = gcon.list_id_in_segment("test", seg0["name"])
        assert not status.OK()
