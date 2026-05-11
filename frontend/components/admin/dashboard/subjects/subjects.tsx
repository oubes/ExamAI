import { motion, AnimatePresence } from "framer-motion";
import { Subject } from "./subject";

import type { Subject as TSubject } from "./types";
import { useState } from "react";

type SubjectsProps = {
	subjects: TSubject[];
	onUpdate: (subjectId: string, updated: Partial<TSubject>) => void;
	onDelete: (subjectId: string) => void;
};

export function Subjects({ subjects, onUpdate, onDelete }: SubjectsProps) {
	const [expandedId, setExpandedId] = useState<string | null>(null);

	function toggleExpand(subjectId: string) {
		setExpandedId((prev) => (prev === subjectId ? null : subjectId));
	}

	return (
		/* ---- List Section ---- */
		<motion.div className="flex flex-col gap-2 w-full">
			<AnimatePresence initial={false} mode="popLayout">
				{subjects.map((subject) => (
					<Subject
						key={subject.id}
						subject={subject}
						onUpdate={(updated) => onUpdate(subject.id, updated)}
						onDelete={() => onDelete(subject.id)}
						expanded={expandedId === subject.id}
						onToggleExpand={() => toggleExpand(subject.id)}
					/>
				))}

				{subjects.length === 0 && (
					<div className="py-20 text-center border-2 border-dashed border-white/5 rounded-3xl">
						<p className="text-zinc-500 font-mono text-sm uppercase tracking-widest">
							No matching records found
						</p>
					</div>
				)}
			</AnimatePresence>
		</motion.div>
	);
}
