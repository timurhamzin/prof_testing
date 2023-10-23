result_scores = adjust_subcategory_scores(
    {
        "mindset": {
            "technical": {
                "Science": 2,
                "Computational": 4,
                "Engineering": 0,
                "total": 6  # Independent total
            },
            "analytical": {
                "Mathematics": 3,
                "Logic": 0,
                "total": 5  # Independent total
            },
            "creative": {
                "Artistic": 1,
                "Innovative": 2,
                "total": 3  # Independent total
            }
        },
        "personality type": {
            "Extraversion": {
                "Social": 3,
                "Talkative": 2,
                "total": 5  # Independent total
            },
            "Introversion": {
                "Reserved": 1,
                "Quiet": 0,
                "total": 3  # Independent total
            },
            "Perceiving": {
                "total": 2
            },
            "Judging": {
                "total": 1
            }
        },
        "academics": {
            "technical": {
                "architecture": 1,
                "software": 1,
                "mechanical": 3,
                "total": 5  # Independent total
            },
            "medical": {
                "healthcare": 1,
                "nursing": 2,
                "total": 3  # Independent total
            },
            "arts": {
                "writing": 1,
                "painting": 0,
                "total": 3  # Independent total
            }
        },
        "interest": {
            "technical": {
                "data analysis": 1,
                "coding": 2,
                "total": 6  # Independent total
            },
            "creative": {
                "visual arts": 1,
                "music": 0,
                "total": 3  # Independent total
            },
            "social sciences": {
                "culture studies": 1,
                "psychology": 2,
                "total": 3  # Independent total
            },
            "engineering": {
                "mechanics": 1,
                "civil": 0,
                "total": 4  # Independent total
            }
        },
        "skills": {
            "communication": {
                "verbal": 2,
                "written": 1,
                "total": 3  # Independent total
            },
            "technical": {
                "programming": 3,
                "hardware": 0,
                "total": 6  # Independent total
            }
        },
    }
)
