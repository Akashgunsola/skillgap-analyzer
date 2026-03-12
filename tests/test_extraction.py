from app.resume.extractor import extract_skills

def test_django_false_positive():
    # "go" should NOT trigger "django"
    text = "i like to go to the park"
    results = extract_skills(text)
    assert "django" not in results
    print("Test passed: 'go' did not trigger 'django'")

def test_django_true_positive():
    # "django" SHOULD trigger "django"
    text = "experience with django framework"
    results = extract_skills(text)
    assert "django" in results
    print("Test passed: 'django' triggered 'django'")

def test_multi_word_alias():
    # "django framework" should be detected
    text = "i use the django framework"
    results = extract_skills(text)
    assert "django" in results
    print("Test passed: 'django framework' triggered 'django'")

if __name__ == "__main__":
    test_django_false_positive()
    test_django_true_positive()
    test_multi_word_alias()
    print("\nAll edge case tests passed!")
