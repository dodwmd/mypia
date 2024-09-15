import React, { useState } from 'react';
import { DragDropContext, Droppable, Draggable, DropResult } from 'react-beautiful-dnd';

interface Task {
  id: string;
  content: string;
  status: 'todo' | 'inProgress' | 'done';
}

const initialTasks: Task[] = [
  { id: '1', content: 'Create project proposal', status: 'todo' },
  { id: '2', content: 'Review client feedback', status: 'inProgress' },
  { id: '3', content: 'Finalize design mockups', status: 'todo' },
  { id: '4', content: 'Update documentation', status: 'done' },
  { id: '5', content: 'Schedule team meeting', status: 'inProgress' },
];

const TaskManagement: React.FC = () => {
  const [tasks, setTasks] = useState(initialTasks);
  const [view, setView] = useState<'list' | 'kanban'>('list');

  const onDragEnd = (result: DropResult) => {
    const { destination, source, draggableId } = result;

    if (!destination) {
      return;
    }

    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    const updatedTasks = Array.from(tasks);
    const [reorderedTask] = updatedTasks.splice(source.index, 1);
    updatedTasks.splice(destination.index, 0, {
      ...reorderedTask,
      status: destination.droppableId as 'todo' | 'inProgress' | 'done',
    });

    setTasks(updatedTasks);
  };

  const renderListView = () => (
    <Droppable droppableId="list">
      {(provided) => (
        <ul
          {...provided.droppableProps}
          ref={provided.innerRef}
          className="space-y-2"
        >
          {tasks.map((task, index) => (
            <Draggable key={task.id} draggableId={task.id} index={index}>
              {(provided) => (
                <li
                  ref={provided.innerRef}
                  {...provided.draggableProps}
                  {...provided.dragHandleProps}
                  className="bg-white p-4 rounded-lg shadow flex items-center justify-between"
                >
                  <span className="text-secondary-700">{task.content}</span>
                  <span className={`text-sm font-medium ${
                    task.status === 'todo' ? 'text-primary-600' :
                    task.status === 'inProgress' ? 'text-accent-600' :
                    'text-green-600'
                  }`}>
                    {task.status === 'todo' ? 'To Do' :
                     task.status === 'inProgress' ? 'In Progress' :
                     'Done'}
                  </span>
                </li>
              )}
            </Draggable>
          ))}
          {provided.placeholder}
        </ul>
      )}
    </Droppable>
  );

  const renderKanbanView = () => (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {(['todo', 'inProgress', 'done'] as const).map((status) => (
        <div key={status} className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4 text-secondary-900">
            {status === 'todo' ? 'To Do' :
             status === 'inProgress' ? 'In Progress' :
             'Done'}
          </h3>
          <Droppable droppableId={status}>
            {(provided) => (
              <ul
                {...provided.droppableProps}
                ref={provided.innerRef}
                className="space-y-2"
              >
                {tasks.filter(task => task.status === status).map((task, index) => (
                  <Draggable key={task.id} draggableId={task.id} index={index}>
                    {(provided) => (
                      <li
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        className="bg-secondary-50 p-3 rounded"
                      >
                        {task.content}
                      </li>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </ul>
            )}
          </Droppable>
        </div>
      ))}
    </div>
  );

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-secondary-900 font-display">Task Management</h1>
        <div className="flex space-x-2">
          <button
            onClick={() => setView('list')}
            className={`px-4 py-2 rounded ${
              view === 'list' ? 'bg-primary-600 text-white' : 'bg-white text-secondary-700'
            }`}
          >
            List View
          </button>
          <button
            onClick={() => setView('kanban')}
            className={`px-4 py-2 rounded ${
              view === 'kanban' ? 'bg-primary-600 text-white' : 'bg-white text-secondary-700'
            }`}
          >
            Kanban View
          </button>
        </div>
      </div>
      <DragDropContext onDragEnd={onDragEnd}>
        {view === 'list' ? renderListView() : renderKanbanView()}
      </DragDropContext>
    </div>
  );
};

export default TaskManagement;
