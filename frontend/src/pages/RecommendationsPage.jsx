import React from 'react';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import {
  SparklesIcon,
  BriefcaseIcon,
  ChartBarSquareIcon,
  ArrowTrendingUpIcon,
} from '@heroicons/react/24/outline';

const SAMPLE_PATHWAYS = [
  {
    title: 'Machine Learning Engineer',
    matchScore: 92,
    salary: '$135,000 – $180,000',
    topSkills: ['PyTorch', 'Python', 'MLOps', 'Distributed Training'],
    gapSkills: ['Kubeflow', 'Model Quantization'],
    demand: 'Very High Growth (+28%)',
  },
  {
    title: 'Full Stack Cloud Architect',
    matchScore: 86,
    salary: '$140,000 – $195,000',
    topSkills: ['React', 'FastAPI', 'Docker', 'AWS'],
    gapSkills: ['Terraform', 'Kubernetes Architecture'],
    demand: 'High Growth (+22%)',
  },
  {
    title: 'Data Systems & Analytics Engineer',
    matchScore: 81,
    salary: '$115,000 – $160,000',
    topSkills: ['SQL', 'Python', 'ETL Pipelines', 'PostgreSQL'],
    gapSkills: ['Apache Spark', 'dbt Data Modeling'],
    demand: 'Steady Demand (+18%)',
  },
];

export const RecommendationsPage = () => {
  return (
    <div className="space-y-6">
      {/* Sprint 2 Banner */}
      <div className="rounded-2xl bg-gradient-to-r from-primary-900 via-secondary-900 to-indigo-900 text-white p-8 shadow-md">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/10 rounded-full text-xs font-semibold mb-3">
          <SparklesIcon className="h-4 w-4 text-secondary-300" />
          <span>Sprint 2 Preview</span>
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight">
          Adaptive Career Recommendations & Gap Analysis
        </h1>
        <p className="mt-2 text-primary-100 max-w-2xl text-sm leading-relaxed">
          The autonomous career intelligence engine is currently fine-tuning multi-layer semantic
          matching models. In Sprint 2, real-time embeddings will dynamically rank live job postings
          against your OCEAN traits, verified skills, and academic achievements.
        </p>
      </div>

      <div>
        <h2 className="text-lg font-bold text-gray-900 mb-1">
          Sample Pathway Projections (Preview Mockup)
        </h2>
        <p className="text-xs text-gray-500 mb-4">
          Below is a preview of the interactive pathway cards arriving in the next sprint.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {SAMPLE_PATHWAYS.map((pathway, idx) => (
            <Card key={idx} className="hover:border-primary-400 transition-all">
              <div className="flex items-start justify-between">
                <div className="p-2.5 bg-primary-50 rounded-lg text-primary-900">
                  <BriefcaseIcon className="h-6 w-6" />
                </div>
                <span className="text-xs font-extrabold text-secondary-700 bg-purple-50 px-2.5 py-1 rounded-full border border-purple-200">
                  {pathway.matchScore}% Match
                </span>
              </div>

              <h3 className="font-bold text-base text-gray-900 mt-4">{pathway.title}</h3>
              <p className="text-xs text-gray-500 mt-0.5">{pathway.salary}</p>

              <div className="mt-4 pt-3 border-t border-gray-100 space-y-2">
                <div>
                  <p className="text-[11px] font-semibold text-gray-400 uppercase">
                    Your Strongest Matches
                  </p>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {pathway.topSkills.map((s, i) => (
                      <Badge key={i} variant="primary" size="sm">
                        {s}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="text-[11px] font-semibold text-gray-400 uppercase">
                    Recommended Gap Closures
                  </p>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {pathway.gapSkills.map((g, i) => (
                      <Badge key={i} variant="warning" size="sm">
                        + {g}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
                <span className="flex items-center gap-1">
                  <ArrowTrendingUpIcon className="h-4 w-4 text-green-600" />
                  {pathway.demand}
                </span>
                <span className="font-semibold text-primary-900 hover:underline cursor-pointer">
                  Learn more →
                </span>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RecommendationsPage;
