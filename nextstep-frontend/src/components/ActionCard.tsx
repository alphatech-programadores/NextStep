interface Props {
    icon: React.ReactNode;
    label: string;
}

export function ActionCard({ icon, label }: Props) {
    return (
        <div className="bg-white shadow-md p-4 rounded-xl border hover:scale-[1.02] transition-transform duration-200 cursor-pointer">
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-3">
                    <span className="text-green-700 text-xl">{icon}</span>
                    <span className="font-semibold text-green-900">{label}</span>
                </div>
                <span className="text-green-700">⌄</span>
            </div>
        </div>
    );
}
