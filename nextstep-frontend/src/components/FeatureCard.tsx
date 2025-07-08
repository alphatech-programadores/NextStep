interface Props {
    icon: React.ReactNode;
    title: string;
    description: string;
}

export function FeatureCard({ icon, title, description }: Props) {
    return (
        <div className="bg-white p-5 rounded-xl shadow hover:shadow-md transition cursor-default">
            <div className="text-green-700 text-3xl mb-3">{icon}</div>
            <h3 className="font-semibold text-green-800 text-lg">{title}</h3>
            <p className="text-sm text-gray-600 mt-1">{description}</p>
        </div>
    );
}
