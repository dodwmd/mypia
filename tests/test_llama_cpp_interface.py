import pytest
from unittest.mock import patch, MagicMock
from personal_ai_assistant.llm.llama_cpp_interface import LlamaCppInterface

@pytest.fixture
def llama_interface():
    with patch('personal_ai_assistant.llm.llama_cpp_interface.Llama') as mock_llama:
        mock_llama.return_value = MagicMock()
        return LlamaCppInterface("/app/static/models/mock_model.gguf")

def test_generate(llama_interface):
    llama_interface.llm.return_value = {'choices': [{'text': ' Generated text'}]}
    
    result = llama_interface.generate("Test prompt")
    
    assert result == "Generated text"
    llama_interface.llm.assert_called_once_with(
        "Test prompt",
        max_tokens=100,
        temperature=0.7,
        stop=["</s>", "\n"],
        echo=False
    )

def test_summarize(llama_interface):
    llama_interface.generate = MagicMock(return_value="Summarized text")
    
    result = llama_interface.summarize("Long text to summarize", max_length=50)
    
    assert result == "Summarized text"
    llama_interface.generate.assert_called_once()
    assert "Summarize the following text in 50 words or less" in llama_interface.generate.call_args[0][0]
