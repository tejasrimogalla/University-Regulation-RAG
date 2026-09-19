import React from 'react';
import {
  GraduationCap,
  ClipboardList,
  BookOpen,
  HeartPulse,
  RefreshCw,
  HelpCircle
} from 'lucide-react';

export default function EmptyState({ onSelectExample }) {
  const examples = [
    {
      topic: 'Attendance Policy',
      question: 'What is the minimum attendance requirement?',
      icon: <ClipboardList size={16} color="#38bdf8" />
    },
    {
      topic: 'Examination Rules',
      question: 'What are the eligibility requirements for semester examinations?',
      icon: <BookOpen size={16} color="#a78bfa" />
    },
    {
      topic: 'Medical Condonation',
      question: 'Can attendance shortage be condoned?',
      icon: <HeartPulse size={16} color="#f472b6" />
    },
    {
      topic: 'Supplementary Exams',
      question: 'What is the supplementary examination rule?',
      icon: <RefreshCw size={16} color="#34d399" />
    },
    {
      topic: 'Out of Scope / Absence Test',
      question: "What is the university's policy on Mars colonization?",
      icon: <HelpCircle size={16} color="#fbbf24" />
    }
  ];

  return (
    <div className="empty-state-container">
      <div className="empty-state-icon">
        <GraduationCap size={44} color="#6366f1" />
      </div>
      <h2>University Regulation Assistant</h2>
      <p className="empty-state-desc">
        Ask questions about academic policies, examination guidelines, attendance rules,
        grading criteria, and student codes of conduct. Answers are strictly grounded in
        uploaded documents with exact page citations.
      </p>

      <div className="example-prompts-section">
        <span className="example-prompts-label">Try asking an example question:</span>
        <div className="example-grid">
          {examples.map((item, idx) => (
            <button
              key={idx}
              className="example-card"
              onClick={() => onSelectExample(item.question)}
            >
              <div className="example-card-top">
                <span className="example-icon-wrapper">{item.icon}</span>
                <span className="example-topic">{item.topic}</span>
              </div>
              <p className="example-question">"{item.question}"</p>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
