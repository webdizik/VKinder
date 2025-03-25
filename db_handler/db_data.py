
import logging
import os
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from db_handler.db_modules import User, Favorite, UserState

# Настройка подключения к PostgreSQL через SQLAlchemy
DSN = 'postgresql://postgres:123@localhost:5432/vkinder'
engine = sqlalchemy.create_engine(DSN) # Инициализация движка БД

# Настройка логирования
log_file = os.path.join(os.path.dirname(__file__),'Logs', 'DB.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def ensure_user_exists(user_id):
    """
    Функция проверяет существование пользователя в таблице users.
    Если пользователь не существует - создается новая запись.
    На вход принимает id пользователя.
    """
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            new_user = User(
                user_id=user_id,
                vk_id=user_id
            )
            session.add(new_user)
            session.commit()
            logging.info(f"Пользователь {user_id} создан.")

    except Exception as e:
        session.rollback()
        logging.error(f"Ошибка при создании пользователя {user_id}: {e}")

    finally:
        session.close()


def save_favorite(user_id, first_name, last_name, vk_link):
    """Функция сохраняет пользователя в избранное."""
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        new_favorite = Favorite(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            vk_link=vk_link
        )
        session.add(new_favorite)
        session.commit()
        logging.info(f"Данные пользователя {vk_link} сохранены в таблицу Favorites.")

    except Exception as e:
        session.rollback()
        logging.error(f"Ошибка при сохранении в избранное пользователя {vk_link}: {e}")

    finally:
        session.close()


def delete_favorite(user_id):
    """Функция удаляет пользователя из избранного."""
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        favorite_to_delete = session.query(Favorite).filter_by(user_id=user_id).first()
        if favorite_to_delete:
            print(f"Найден пользователь: {favorite_to_delete.__dict__}")  # Отладочный вывод
            session.delete(favorite_to_delete)
            session.commit()
            logging.info(f"Данные пользователя c user_id {user_id} удалены из таблицы Favorites.")
        else:
            logging.warning("Пользователь не найден.")

    except Exception as e:
        session.rollback()
        logging.error(f"Ошибка при удалении данных пользователя {user_id}: {e}")

    finally:
        session.close()


def get_favorites_from_db(user_id):
    """Возвращает список избранных кандидатов для пользователя."""
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        favorites = session.query(Favorite).filter_by(user_id=user_id).all()
        favorites_list = [
            {
                'first_name': fav.first_name,
                'last_name': fav.last_name,
                'vk_link': fav.vk_link
            }
            for fav in favorites
        ]
        return favorites_list

    except Exception as e:
        logging.error(f"Ошибка при получении избранных кандидатов для пользователя {user_id}: {e}")
        return []

    finally:
        session.close()


def save_user_state(user_id, current_index, offset, candidates):
    """Сохраняет текущее состояние пользователя (индекс, оффсет, кандидатов)."""
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        user_state = session.query(UserState).filter_by(user_id=user_id).first()
        if user_state:
            user_state.current_index = current_index
            user_state.offset = offset
            user_state.candidates = candidates
        else:
            new_user_state = UserState(
                user_id=user_id,
                current_index=current_index,
                offset=offset,
                candidates=candidates
            )
            session.add(new_user_state)
        session.commit()
        logging.info(f"Состояние пользователя {user_id} сохранено.")

    except Exception as e:
        session.rollback()
        logging.error(f"Ошибка при сохранении состояния пользователя {user_id}: {e}")

    finally:
        session.close()


def load_user_state(user_id):
    """Загружает сохраненное состояние пользователя."""
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        user_state = session.query(UserState).filter_by(user_id=user_id).first()

        if user_state:
            return {
                'current_index': user_state.current_index,
                'offset': user_state.offset,
                'candidates': user_state.candidates
            }
        else:
            return None  # Если запись не найдена

    except Exception as e:
        logging.error(f"Ошибка при загрузке состояния пользователя {user_id}: {e}")
        return None

    finally:
        session.close()
