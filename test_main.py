"""경조사 가이드 검증 테스트 (python -m unittest test_main -v)
기대값은 수집한 출처 수치와 별도로 직접 입력해 대조합니다."""
import inspect
import unittest

import main


class Wedding(unittest.TestCase):
    def test_default(self):
        r = main.get_wedding_gift_guide()
        self.assertIn("97,900원", r)
        self.assertIn("10만원 65.3%", r)
        self.assertIn("5만원 이하 21.9%", r)
        self.assertIn("호텔 예식 응답: 10만원 55.9%, 15만원 18.7%, 20만원 15.2%", r)
        self.assertIn("정답이 없습니다", r)

    def test_range_by_closeness_and_venue(self):
        self.assertIn("10만 원 (설문에서 가장 많이", main.get_wedding_gift_guide("보통"))
        self.assertIn("10만~20만 원", main.get_wedding_gift_guide("가까운 사이"))
        self.assertIn("5만~10만 원", main.get_wedding_gift_guide("가벼운 관계"))
        self.assertIn("호텔 예식은 식대 부담", main.get_wedding_gift_guide("보통", "호텔"))
        self.assertNotIn("호텔 예식은 식대 부담", main.get_wedding_gift_guide("보통", "일반"))

    def test_not_attending_and_invalid(self):
        self.assertIn("참석하지 않을 때의 별도 통계는 확보하지 못했습니다", main.get_wedding_gift_guide(attending=False))
        self.assertTrue(main.get_wedding_gift_guide("친구").startswith("[입력 확인]"))
        self.assertTrue(main.get_wedding_gift_guide("보통", "야외").startswith("[입력 확인]"))

    def test_sums(self):
        self.assertAlmostEqual(sum(v for _, v in main.WEDDING["dist"]), 99.2, places=1)
        self.assertAlmostEqual(main.WEDDING["dist"][2][1] + main.WEDDING["dist"][3][1], 12.0, places=1)
        self.assertAlmostEqual(main.WEDDING["hotel"][1][1] + main.WEDDING["hotel"][2][1], 33.9, places=1)


class Condolence(unittest.TestCase):
    def test_default_and_age(self):
        r = main.get_condolence_gift_guide()
        self.assertIn("95,300원", r)
        self.assertIn("10만원 61.8%", r)
        self.assertIn("20대 89,000원", r)
        r2 = main.get_condolence_gift_guide("보통", "60대 이상")
        self.assertIn("(60대 이상) 평균: 108,400원", r2)
        self.assertIn("부의(賻儀)", r2)

    def test_invalid(self):
        self.assertTrue(main.get_condolence_gift_guide("보통", "10대").startswith("[입력 확인]"))
        self.assertTrue(main.get_condolence_gift_guide("남").startswith("[입력 확인]"))

    def test_range(self):
        self.assertIn("5만~10만 원", main.get_condolence_gift_guide("가벼운 관계"))
        self.assertIn("(15만·20만 원 합계 11.8%)", main.get_condolence_gift_guide("가까운 사이"))
        self.assertAlmostEqual(main.CONDOLENCE["dist"][2][1] + main.CONDOLENCE["dist"][3][1], 11.8, places=1)


class Limits(unittest.TestCase):
    def test_limits(self):
        r = main.get_official_gift_limits()
        self.assertIn("50,000원", r)
        self.assertIn("100,000원", r)
        self.assertIn("일반 개인 간", r)


class Leave(unittest.TestCase):
    def test_public(self):
        self.assertIn("5일", main.get_condolence_leave_days("본인 결혼", "공무원"))
        self.assertIn("1일", main.get_condolence_leave_days("자녀 결혼", "공무원"))
        self.assertIn("3일", main.get_condolence_leave_days("조부모 사망", "공무원"))
        self.assertIn("본인 및 배우자의 부모", main.get_condolence_leave_days("부모 사망", "공무원"))
        self.assertIn("토요일과 공휴일", main.get_condolence_leave_days("부모 사망", "공무원"))

    def test_private(self):
        r = main.get_condolence_leave_days("부모 사망")
        self.assertIn("법정 경조사 휴가가 없습니다", r)
        self.assertIn("5일", r)
        r2 = main.get_condolence_leave_days("배우자 출산", "민간")
        self.assertIn("유급 20일", r2)
        self.assertIn("120일", r2)

    def test_invalid(self):
        self.assertTrue(main.get_condolence_leave_days("이혼").startswith("[입력 확인]"))
        self.assertTrue(main.get_condolence_leave_days("본인 결혼", "회사").startswith("[입력 확인]"))
        self.assertEqual(len(main.LEAVE_PUBLIC), 8)


class Reference(unittest.TestCase):
    def test_reference(self):
        r = main.get_guide_reference()
        for s in ("2026-11-04", "틸리언 프로", "청탁금지법", "복무규정", "관계별 공식 통계가 아닙니다"):
            self.assertIn(s, r)


class Registry(unittest.TestCase):
    def test_tools(self):
        import fastmcp
        reg = getattr(fastmcp, "REG", None)
        if reg is None:
            self.skipTest("등록 정보 검사는 테스트용 스텁 fastmcp에서만 실행합니다")
        self.assertEqual(set(reg), {"get_wedding_gift_guide", "get_condolence_gift_guide", "get_official_gift_limits",
                                    "get_condolence_leave_days", "get_guide_reference"})
        for name, (kw, fn) in reg.items():
            self.assertEqual(set(kw["annotations"]),
                             {"title", "readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"})
            self.assertLessEqual(len(kw["description"]), 1024, name)
            self.assertIn("경조사 가이드 - Event Money Guide", kw["description"])
            self.assertNotIn("kakao", name.lower())
            self.assertTrue(inspect.signature(fn).parameters is not None)
        self.assertLessEqual(len(main.SERVICE), 30)


if __name__ == "__main__":
    unittest.main()
