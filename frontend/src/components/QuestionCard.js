import React, { useState } from 'react';
import { Card, Button, Form, Alert } from 'react-bootstrap';

const QuestionCard = ({ question, onAnswer, loading, feedback, isCorrect }) => {
  const [answer, setAnswer] = useState('');
  const [selectedOption, setSelectedOption] = useState(null);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.type === 'objective') {
      onAnswer(selectedOption.toString());
    } else {
      onAnswer(answer);
    }
    setAnswer('');
    setSelectedOption(null);
  };
  
  return (
    <Card className="mb-4 shadow-sm">
      <Card.Header className="bg-primary text-white">
        <h5 className="mb-0">❓ Question</h5>
      </Card.Header>
      <Card.Body>
        <p className="lead mb-4">{question.text}</p>
        
        {question.type === 'objective' ? (
          // Multiple choice options
          <Form onSubmit={handleSubmit}>
            {question.options.map((option, index) => (
              <Form.Check
                key={index}
                type="radio"
                id={`option-${index}`}
                label={option}
                name="questionOptions"
                className="mb-3"
                checked={selectedOption === index}
                onChange={() => setSelectedOption(index)}
                disabled={loading || feedback}
              />
            ))}
            <Button 
              type="submit" 
              variant="primary" 
              disabled={loading || selectedOption === null || feedback}
              className="mt-3"
            >
              {loading ? 'Checking...' : 'Submit Answer'}
            </Button>
          </Form>
        ) : (
          // Subjective question input
          <Form onSubmit={handleSubmit}>
            <Form.Group>
              <Form.Control
                as="textarea"
                rows={4}
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Type your answer here..."
                disabled={loading || feedback}
              />
            </Form.Group>
            <Button 
              type="submit" 
              variant="primary" 
              disabled={loading || !answer.trim() || feedback}
              className="mt-3"
            >
              {loading ? 'Checking...' : 'Submit Answer'}
            </Button>
          </Form>
        )}
        
        {feedback && (
          <Alert 
            variant={isCorrect ? 'success' : 'danger'} 
            className="mt-4"
          >
            <div dangerouslySetInnerHTML={{ __html: feedback.replace(/\n/g, '<br/>') }} />
          </Alert>
        )}
        
        {question.type === 'objective' && feedback && question.explanation && (
          <Alert variant="info" className="mt-3">
            <strong>Explanation:</strong>
            <div dangerouslySetInnerHTML={{ __html: question.explanation.replace(/\n/g, '<br/>') }} />
          </Alert>
        )}
      </Card.Body>
    </Card>
  );
};

export default QuestionCard; 